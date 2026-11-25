# -*- coding: utf-8 -*-
"""core.coordinator: 4-layer lifecycle coordinator for Smart Shutdown."""

import time, queue, logging, threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from core.config import SettingsConfig, release_single_instance_lock
from core.models import LifecycleState, TargetMode, AntiGravityAIState, TelemetryEvent, UserCommand, DEFAULT_SIMULATION_SECONDS, resolve_mode_duration_seconds
import core.input_hook as input_hook, core.process_tree as process_tree
import core.waiting_gate as waiting_gate, core.app_closer as app_closer, core.shutdown_dispatcher as shutdown_dispatcher
from core.telemetry_collector import TelemetryCollector, evaluate_hardware_block
from core.transcript_sentinel import TranscriptSentinel

logger_instance = logging.getLogger("SmartShutdown")
_EXEC_MODE_MAP = {"Demo (30s)": TargetMode.DEMO_30S, "Demo (10s)": TargetMode.DEMO_10S, "Simulation": TargetMode.SIMULATION, "Live": TargetMode.LIVE}


def _resolve_target_mode(mode: Union[TargetMode, str]) -> TargetMode:
    if isinstance(mode, TargetMode): return mode
    m = str(mode).upper()
    for token, target in (("30", TargetMode.DEMO_30S), ("10", TargetMode.DEMO_10S), ("DEMO", TargetMode.DEMO_30S)):
        if token in m: return target
    return TargetMode.SIMULATION if ("SIM" in m or "DRY" in m) else TargetMode.LIVE


class SentinelCoordinator:
    """Coordinates redundant tracking lifecycle and executes application closing & shutdown."""

    def __init__(self, config: Optional[SettingsConfig] = None, brain_dir: Optional[Path] = None, dry_run: bool = False, logger: Optional[logging.Logger] = None):
        self.config = config or SettingsConfig(); self.config.clamp()
        self.brain_dir, self.logger = brain_dir, logger or logger_instance
        if dry_run:
            self.target_mode, self.dry_run = TargetMode.SIMULATION, True
        else:
            self.target_mode = _EXEC_MODE_MAP.get(getattr(self.config, "execution_mode", "Live"), TargetMode.LIVE)
            self.dry_run = self.target_mode in (TargetMode.SIMULATION, TargetMode.DEMO_10S)

        self.state, self.ai_state = LifecycleState.IDLE_MONITORING, AntiGravityAIState.READY.value
        self._loop_counter = 0
        self.remaining_countdown_seconds = self._default_mode_seconds()
        self.baseline_input_tick = input_hook.get_last_input_tick()
        self.apps_closed = self.shutdown_dispatched = False
        self.closed_apps_list: List[Dict[str, Any]] = []
        self._last_active_count, self._last_subagent_count, self._last_summary = 0, 0, ""
        self._telemetry_collector, self._last_hw_telemetry = TelemetryCollector(), {}
        self.event_queue, self.command_queue = queue.Queue(), queue.Queue()
        self.is_paused, self.bypass_inhibitors = False, False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event, self._demo_timer, self._state_lock = threading.Event(), None, threading.RLock()

    def _default_mode_seconds(self) -> int:
        return resolve_mode_duration_seconds(self.target_mode, self.config.master_shutdown_timer_min, getattr(self.config, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS))

    def _effective_grace_window(self) -> int:
        if self.target_mode == TargetMode.DEMO_30S: return 10
        if self.target_mode == TargetMode.SIMULATION: return min(10, self._default_mode_seconds())
        if self.target_mode == TargetMode.DEMO_10S: return min(2, int(self.config.pre_shutdown_close_window_sec))
        return int(self.config.pre_shutdown_close_window_sec)

    def effective_user_inactivity_threshold(self) -> float:
        return 10.0 if self.target_mode in (TargetMode.DEMO_30S, TargetMode.DEMO_10S) else float(self.config.user_inactivity_sec)

    def set_target_mode(self, mode: Union[TargetMode, str]) -> TargetMode:
        """Switch between LIVE, DEMO_30S, DEMO_10S, and SIMULATION modes."""
        self.target_mode = _resolve_target_mode(mode)
        if self._demo_timer and self._demo_timer.is_alive():
            self._demo_timer.cancel(); self._demo_timer = None
        if self.apps_closed:
            shutdown_dispatcher.abort_shutdown(dry_run=self.dry_run, logger=self.logger); self.apps_closed = False
        self.dry_run = self.target_mode in (TargetMode.SIMULATION, TargetMode.DEMO_10S)
        self.state = LifecycleState.IDLE_MONITORING
        self.is_paused = self.shutdown_dispatched = False
        self.remaining_countdown_seconds = self._default_mode_seconds()
        self.baseline_input_tick = input_hook.get_last_input_tick()
        payload = self._state_payload(remaining=self.remaining_countdown_seconds, is_paused=self.is_paused, mode=self.target_mode.value)
        for ev in ("STATE_CHANGE", "TELEMETRY", "MODE_CHANGE"): self.emit_event(ev, payload)
        self.logger.info(f"[COORDINATOR] Mode -> {self.target_mode.value} (dry_run={self.dry_run})")
        return self.target_mode

    def toggle_bypass_inhibitors(self) -> bool:
        self.bypass_inhibitors = not self.bypass_inhibitors
        self.emit_event("TELEMETRY", self._state_payload(bypass_inhibitors=self.bypass_inhibitors)); return self.bypass_inhibitors

    def attach_event_queue(self, event_q: queue.Queue) -> None: self.event_queue = event_q
    def post_command(self, cmd: UserCommand) -> None: self.command_queue.put_nowait(cmd)

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        try: self.event_queue.put_nowait(TelemetryEvent(event_type=event_type, timestamp=time.time(), data=data))
        except Exception: pass

    def _emit_state(self, **kwargs: Any) -> None: self.emit_event("STATE_CHANGE", self._state_payload(**kwargs))
    def _emit_ai(self, **kwargs: Any) -> None: self.emit_event("AI_STATE_CHANGE", {"ai_state": self.ai_state, "workers": self._last_subagent_count, **kwargs})

    def _read_idle_seconds(self) -> float:
        try: return float(getattr(input_hook, "get_user_idle_seconds", input_hook.get_idle_seconds)())
        except Exception: return 0.0

    def _state_payload(self, **kwargs: Any) -> Dict[str, Any]:
        eff_thresh, idle_sec = int(self.effective_user_inactivity_threshold()), self._read_idle_seconds()
        p = {
            "state": self.state.value if isinstance(self.state, LifecycleState) else str(self.state),
            "target_mode": self.target_mode.value, "mode": self.target_mode.value,
            "is_demo": self.target_mode in (TargetMode.DEMO_30S, TargetMode.DEMO_10S), "is_paused": self.is_paused,
            "active_count": self._last_active_count, "subagent_count": self._last_subagent_count, "workers": self._last_subagent_count,
            "dry_run": self.dry_run, "idle_sec": round(idle_sec, 1),
            "has_user_input": bool(self.baseline_input_tick and input_hook.get_last_input_tick() > self.baseline_input_tick),
            "idle_threshold": eff_thresh, "inactivity_threshold_sec": eff_thresh,
            "idle_remaining_sec": max(0, eff_thresh - int(idle_sec)),
            "idle_pct": round(max(0.0, min(1.0, idle_sec / max(1, eff_thresh))), 3),
            "remaining": self.remaining_countdown_seconds, "remaining_seconds": self.remaining_countdown_seconds,
            "total_seconds": self._default_mode_seconds(), "target_action": getattr(self.config, "target_action", "Shutdown"),
        }
        p.update(kwargs); return p

    def _build_telemetry_payload(self, hw: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        hw_data = dict(hw if hw is not None else self._last_hw_telemetry)
        hw_data.setdefault("is_tree_busy", False)
        return self._state_payload(**hw_data, is_paused=self.is_paused, waiting_mode=self.config.waiting_mode, bypass_inhibitors=self.bypass_inhibitors, ai_state=self.ai_state)

    def _get_waiting_mode_enum(self) -> waiting_gate.WaitingMode:
        m = (self.config.waiting_mode or "").strip().lower()
        if "unlimited" in m: return waiting_gate.WaitingMode.UNLIMITED
        return waiting_gate.WaitingMode.FIXED_TIMER if "timer" in m else waiting_gate.WaitingMode.HYBRID

    def step_user_inactivity_check(self) -> bool:
        """Step 1: Check physical inactivity. Transitions to AI_EVALUATION when idle."""
        if self.target_mode in (TargetMode.DEMO_30S, TargetMode.DEMO_10S) and self.state in (LifecycleState.COUNTDOWN_ACTIVE, LifecycleState.PRE_SHUTDOWN_GRACE):
            return True
        thresh = self.effective_user_inactivity_threshold()
        if input_hook.is_user_idle(threshold_seconds=thresh):
            self.state = LifecycleState.AI_EVALUATION
            self.logger.info(f"[COORDINATOR] User idle (>= {thresh}s) -> {self.state.value}.")
            self._emit_state(reason="user_idle"); return True
        if self.state != LifecycleState.IDLE_MONITORING:
            self.state = LifecycleState.IDLE_MONITORING; self._emit_state(reason="user_active")
        return False

    def _evaluate_waiting_gates(self, eval_res: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mode, hybrid_timeout = self._get_waiting_mode_enum(), float(self.config.waiting_hybrid_timeout_min * 60)
        for session in eval_res.get("sessions", []):
            if session.get("status") != "WAITING_USER": continue
            gate_res = waiting_gate.evaluate_waiting_state(session_state=session, mode=mode, timeout_seconds=hybrid_timeout)
            if gate_res.should_block_shutdown:
                self.state, self.ai_state = LifecycleState.WAITING_USER_PROMPT, AntiGravityAIState.INPUT_PENDING.value
                self.logger.info(f"[COORDINATOR] Waiting user prompt: {gate_res.details}")
                self._emit_state(reason="waiting_user_input", details=gate_res.details); self._emit_ai(details=gate_res.details)
                return {"status": "WAITING_USER_BLOCKED", "gate_res": gate_res, "eval_res": eval_res}
        return None

    def _evaluate_system_blockers(self, eval_res: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.bypass_inhibitors: return None
        if process_tree.is_process_tree_busy():
            self.state = LifecycleState.AI_EVALUATION; self._emit_state(reason="process_tree_busy")
            return {"status": "AI_BUSY_PROCESS", "eval_res": eval_res}
        if eval_res.get("active_count", 0) > 0:
            self.state, self.ai_state = LifecycleState.AI_EVALUATION, AntiGravityAIState.WORKING.value
            self._emit_ai(reason="transcripts_active", active_count=self._last_active_count, subagent_count=self._last_subagent_count)
            return {"status": "AI_BUSY_TRANSCRIPT", "eval_res": eval_res}
        hw_reason = evaluate_hardware_block(self._last_hw_telemetry, self.config)
        if hw_reason:
            self.state = LifecycleState.AI_EVALUATION; self.logger.info(f"[COORDINATOR] Inhibited by {hw_reason}.")
            self._emit_state(reason=hw_reason); return {"status": "HW_BUSY_INHIBITED", "reason": hw_reason, "eval_res": eval_res}
        return None

    def _update_ai_snapshot(self, eval_res: Dict[str, Any], emit: bool = True) -> None:
        self._last_active_count, self._last_subagent_count, self._last_summary = eval_res.get("active_count", 0), eval_res.get("subagent_count", 0), eval_res.get("summary", "")
        active_ai = self._last_active_count > 0 or self._last_subagent_count > 0
        new_ai = AntiGravityAIState.INPUT_PENDING.value if eval_res.get("waiting_count", 0) > 0 else (AntiGravityAIState.WORKING.value if active_ai else AntiGravityAIState.READY.value)
        if emit or new_ai != self.ai_state:
            self.ai_state = new_ai
            self._emit_ai(summary=self._last_summary, active_count=self._last_active_count, subagent_count=self._last_subagent_count)

    def step_ai_evaluation(self, idle_buffer: int = 30) -> Dict[str, Any]:
        """Step 2: Inspect transcripts, process tree, waiting gates, and hardware limits."""
        eval_res = TranscriptSentinel(brain_dir=self.brain_dir, logger=self.logger).evaluate_all(idle_buffer=idle_buffer)
        self._update_ai_snapshot(eval_res, emit=True)
        for check in (self._evaluate_waiting_gates, self._evaluate_system_blockers):
            blocked = check(eval_res)
            if blocked: return blocked
        self.state, self.ai_state = LifecycleState.COUNTDOWN_ACTIVE, AntiGravityAIState.READY.value
        self.remaining_countdown_seconds, self.baseline_input_tick = self._default_mode_seconds(), input_hook.get_last_input_tick()
        self.logger.info(f"[COORDINATOR] Armed countdown: {self.remaining_countdown_seconds}s.")
        self._emit_ai(reason="all_tasks_complete", active_count=0, subagent_count=0)
        self._emit_state(remaining=self.remaining_countdown_seconds)
        return {"status": "READY_COUNTDOWN", "eval_res": eval_res}

    def check_physical_interrupt(self, current_tick: Optional[int] = None) -> bool:
        """Check for physical mouse/keyboard activity during countdown."""
        if self.is_paused:
            return False
        curr = current_tick if current_tick is not None else input_hook.get_last_input_tick()
        if self.baseline_input_tick > 0 and curr > self.baseline_input_tick:
            self.logger.warning(f"[COORDINATOR] Physical input detected ({curr} > {self.baseline_input_tick}).")
            if self.apps_closed: shutdown_dispatcher.abort_shutdown(dry_run=self.dry_run, logger=self.logger)
            self.remaining_countdown_seconds, self.apps_closed = self._default_mode_seconds(), False
            self.state, self.baseline_input_tick = LifecycleState.IDLE_MONITORING, curr
            self._emit_state(reason="physical_interrupt"); return True
        return False

    def _close_apps_for_shutdown(self) -> None:
        app_targets, close_ag = getattr(self.config, "app_closing_targets", None), getattr(self.config, "close_antigravity", True)
        self.closed_apps_list = app_closer.close_user_applications(dry_run=self.dry_run, logger=self.logger, app_targets=app_targets, close_antigravity=close_ag, config=self.config)
        app_closer.close_antigravity_cleanly(dry_run=self.dry_run, logger=self.logger, enabled=close_ag)
        self.apps_closed = True

    def _dispatch_power_action(self) -> bool:
        action = getattr(self.config, "target_action", "Shutdown")
        if action == "Shutdown": return shutdown_dispatcher.execute_shutdown(dry_run=self.dry_run, delay_seconds=0, logger=self.logger)
        return shutdown_dispatcher.execute_shutdown(dry_run=self.dry_run, delay_seconds=0, logger=self.logger, target_action=action)

    def _handle_grace_closing(self, grace_window: int) -> None:
        self.state = LifecycleState.PRE_SHUTDOWN_GRACE
        self.logger.warning(f"[COORDINATOR] Grace window ({self.remaining_countdown_seconds}s <= {grace_window}s). Broadcasting WM_CLOSE.")
        self._close_apps_for_shutdown(); self._emit_state(apps_closed=True)

    def _flush_before_power_action(self) -> None:
        """Flush log handlers and release single-instance lock prior to OS power action."""
        if self.dry_run:
            return
        for handler in list(getattr(self.logger, "handlers", [])):
            try:
                handler.flush()
            except Exception:
                pass
        try:
            release_single_instance_lock(logger=self.logger)
        except Exception:
            pass

    def _handle_countdown_zero(self) -> None:
        self.state = LifecycleState.SHUTDOWN_EXECUTED
        self.logger.critical("[COORDINATOR] Countdown 00:00! Dispatching power action.")
        self._flush_before_power_action()
        self.shutdown_dispatched = self._dispatch_power_action(); self._emit_state(shutdown_dispatched=self.shutdown_dispatched)
        if self.target_mode in (TargetMode.SIMULATION, TargetMode.DEMO_30S, TargetMode.DEMO_10S) or self.dry_run:
            self._schedule_demo_reset()

    def tick_countdown(self, step_seconds: int = 1) -> Dict[str, Any]:
        """Advance the countdown timer unless paused."""
        if self.state not in (LifecycleState.COUNTDOWN_ACTIVE, LifecycleState.PRE_SHUTDOWN_GRACE):
            return {"state": self.state, "remaining": self.remaining_countdown_seconds}
        if not self.is_paused: self.remaining_countdown_seconds = max(0, self.remaining_countdown_seconds - step_seconds)
        grace = self._effective_grace_window()
        if self.remaining_countdown_seconds <= grace and not self.apps_closed and not self.is_paused: self._handle_grace_closing(grace)
        if self.remaining_countdown_seconds <= 0 and not self.shutdown_dispatched and not self.is_paused: self._handle_countdown_zero()
        res = self._state_payload(remaining=self.remaining_countdown_seconds, apps_closed=self.apps_closed, shutdown_dispatched=self.shutdown_dispatched, is_paused=self.is_paused, grace=grace)
        self.emit_event("TICK", res); return res

    def start_countdown(self, seconds: Optional[int] = None) -> None:
        if seconds is not None: self.remaining_countdown_seconds = int(seconds)
        self.state, self.is_paused, self.baseline_input_tick = LifecycleState.COUNTDOWN_ACTIVE, False, input_hook.get_last_input_tick()
        self.logger.info(f"[COORDINATOR] Countdown started: {self.remaining_countdown_seconds}s.")
        self._emit_state(remaining=self.remaining_countdown_seconds, is_paused=False)

    def pause_countdown(self) -> None:
        with self._state_lock:
            self.is_paused = True
            self.baseline_input_tick = input_hook.get_last_input_tick()
            self._emit_state(remaining=self.remaining_countdown_seconds, is_paused=True)

    def resume_countdown(self) -> None:
        with self._state_lock:
            self.is_paused = False
            self.baseline_input_tick = input_hook.get_last_input_tick()
            if self.state == LifecycleState.IDLE_MONITORING: self.state = LifecycleState.COUNTDOWN_ACTIVE
            self._emit_state(remaining=self.remaining_countdown_seconds, is_paused=False)

    def snooze_countdown(self, seconds: int = 300) -> int:
        with self._state_lock:
            self.remaining_countdown_seconds += int(seconds)
            self.baseline_input_tick = input_hook.get_last_input_tick()
            if self.state == LifecycleState.PRE_SHUTDOWN_GRACE and self.remaining_countdown_seconds > self._effective_grace_window():
                if self.apps_closed:
                    shutdown_dispatcher.abort_shutdown(dry_run=self.dry_run, logger=self.logger); self.apps_closed = False
                self.state = LifecycleState.COUNTDOWN_ACTIVE
                self._emit_state(reason="snoozed", remaining=self.remaining_countdown_seconds, is_paused=self.is_paused)
            self.emit_event("TICK", self._state_payload(remaining=self.remaining_countdown_seconds, is_paused=self.is_paused))
            return self.remaining_countdown_seconds

    def _schedule_demo_reset(self, delay_sec: float = 5.0) -> None:
        if self._demo_timer and self._demo_timer.is_alive(): self._demo_timer.cancel()
        self._demo_timer = threading.Timer(delay_sec, self.reset_to_idle, kwargs={"reason": "demo_completed"})
        self._demo_timer.daemon = True; self._demo_timer.start()

    def reset_to_idle(self, reason: str = "demo_completed") -> None:
        self.is_paused = self.apps_closed = self.shutdown_dispatched = False
        self.state, self.remaining_countdown_seconds, self.baseline_input_tick = LifecycleState.IDLE_MONITORING, self._default_mode_seconds(), input_hook.get_last_input_tick()
        self._emit_state(reason=reason, remaining=self.remaining_countdown_seconds)

    def cancel_and_reset(self) -> None:
        if self.apps_closed: shutdown_dispatcher.abort_shutdown(dry_run=self.dry_run, logger=self.logger)
        self.reset_to_idle(reason="user_cancelled")

    def force_shutdown_now(self) -> None:
        self.logger.warning("[COORDINATOR] Force shutdown requested.")
        if not self.apps_closed: self._close_apps_for_shutdown()
        self.remaining_countdown_seconds, self.state = 0, LifecycleState.SHUTDOWN_EXECUTED
        self._flush_before_power_action()
        self.shutdown_dispatched = self._dispatch_power_action()
        self._emit_state(shutdown_dispatched=self.shutdown_dispatched)
        if self.target_mode in (TargetMode.SIMULATION, TargetMode.DEMO_30S, TargetMode.DEMO_10S) or self.dry_run:
            self._schedule_demo_reset()

    def update_config(self, new_config: SettingsConfig) -> None:
        self.config = new_config; self.config.clamp()
        if self.state == LifecycleState.IDLE_MONITORING: self.remaining_countdown_seconds = self._default_mode_seconds()
        self.emit_event("CONFIG_UPDATED", self.config.to_dict())
        self.emit_event("TELEMETRY", self._build_telemetry_payload())

    def start_background_loop(self, poll_interval: float = 1.0) -> None:
        if self._worker_thread is not None and self._worker_thread.is_alive(): return
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._background_run_loop, args=(poll_interval,), daemon=True, name="SentinelCoordinatorWorker")
        self._worker_thread.start()

    def stop_background_loop(self, timeout: float = 2.0) -> None:
        self._stop_event.set()
        if self._worker_thread is not None and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=timeout); self._worker_thread = None

    def _execute_command(self, cmd: UserCommand) -> None:
        t, payload = cmd.command_type, cmd.payload or {}
        dispatch = {"PAUSE": self.pause_countdown, "RESUME": self.resume_countdown, "CANCEL": self.cancel_and_reset, "FORCE_SHUTDOWN": self.force_shutdown_now}
        if t in dispatch: dispatch[t](); return
        if t == "SNOOZE": self.snooze_countdown(payload.get("seconds", 300))
        elif t == "UPDATE_CONFIG" and cmd.payload: self.update_config(SettingsConfig.from_dict(payload))
        elif t == "SET_MODE" and cmd.payload: self.set_target_mode(payload.get("mode", "LIVE"))

    def _process_pending_commands(self) -> None:
        while not self.command_queue.empty():
            try: self._execute_command(self.command_queue.get_nowait())
            except Exception as e: self.logger.error(f"[COORDINATOR] Command error: {e}")

    def _poll_ai_state(self) -> None:
        try: self._update_ai_snapshot(TranscriptSentinel(brain_dir=self.brain_dir, logger=self.logger).evaluate_all(idle_buffer=30), emit=False)
        except Exception: pass

    def _step_background_state(self) -> None:
        if self.is_paused:
            return
        if self.state in (LifecycleState.COUNTDOWN_ACTIVE, LifecycleState.PRE_SHUTDOWN_GRACE):
            self.check_physical_interrupt(); self.tick_countdown(1); return
        if self.state == LifecycleState.IDLE_MONITORING:
            self.step_user_inactivity_check(); return
        if self.state in (LifecycleState.AI_EVALUATION, LifecycleState.WAITING_USER_PROMPT):
            if not input_hook.is_user_idle(threshold_seconds=self.effective_user_inactivity_threshold()):
                self.step_user_inactivity_check()
            elif self.state == LifecycleState.AI_EVALUATION or self._loop_counter % 2 == 0:
                self.step_ai_evaluation()

    def _interruptible_sleep(self, duration: float, step: float = 0.2) -> None:
        for _ in range(max(1, int(duration / step))):
            if self._stop_event.is_set(): break
            time.sleep(step)

    def _background_run_loop(self, poll_interval: float) -> None:
        while not self._stop_event.is_set():
            try:
                self._process_pending_commands()
                self._last_hw_telemetry = self._telemetry_collector.sample(self.config)
                with self._state_lock:
                    self._step_background_state()
                    if self._loop_counter % 2 == 0 and self.state not in (LifecycleState.AI_EVALUATION, LifecycleState.WAITING_USER_PROMPT):
                        self._poll_ai_state()
                    self._loop_counter += 1
                    self.emit_event("TELEMETRY", self._build_telemetry_payload(self._last_hw_telemetry))
            except Exception as exc:
                self.logger.error(f"[COORDINATOR] Worker loop error: {exc}")
            self._interruptible_sleep(poll_interval, 0.2)


__all__ = ["LifecycleState", "TargetMode", "AntiGravityAIState", "TelemetryEvent", "UserCommand", "SentinelCoordinator"]
