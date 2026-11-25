# -*- coding: utf-8 -*-
"""gui.app_event_bridge: Coordinator event, logging queue bridge, and lifecycle helpers."""

import logging, queue, threading, time
from typing import Any, Dict, Optional, Tuple

from core import input_hook
from core.app_closer import is_running_under_test
from core.config import SettingsConfig, save_settings_config
from core.models import DEFAULT_SIMULATION_SECONDS, TargetMode, TelemetryEvent, resolve_mode_duration_seconds
from core.startup import is_startup_enabled, enable_startup, disable_startup, startup_matches_settings, reconcile_startup_shortcut
from core.system_tray import stop_tray_icon
from gui.components.status_resolver import ResolvedPillState, resolve_ai_pill_state, resolve_hud_mode_label
from gui.theme import STATUS_GREEN

MODE_STR_TO_ENUM = {"Live": TargetMode.LIVE, "Demo (30s)": TargetMode.DEMO_30S, "Demo (10s)": TargetMode.DEMO_10S, "Simulation": TargetMode.SIMULATION}
MODE_ENUM_TO_STR = {v: k for k, v in MODE_STR_TO_ENUM.items()}
_BLOCKER_TITLES = {"process_tree_busy": "AI Process Tree Busy", "hardware_busy": "Hardware Activity Inhibitor", "cpu_busy": "CPU Threshold Inhibitor", "network_busy": "Network Threshold Inhibitor", "audio_active": "Audio Stream Inhibitor Active", "waiting_user_input": "Waiting for User Input"}


class GuiLogQueueHandler(logging.Handler):
    """Thread-safe logging handler forwarding backend logs into coordinator LOG events."""

    def __init__(self, coordinator: Any, level: int = logging.INFO) -> None:
        super().__init__(level); self._coordinator, self._local = coordinator, threading.local()

    def set_coordinator(self, coordinator: Any) -> None: self._coordinator = coordinator

    @staticmethod
    def _resolve_level(record: logging.LogRecord, message: str) -> str:
        if record.levelno >= logging.ERROR: return "crit"
        if record.levelno >= logging.WARNING: return "warn"
        upper = message.upper()
        if any(tok in upper for tok in ("[HEALTH]", "[TELEMETRY]", "[AUDIO", "[HW_")): return "health"
        if any(tok in upper for tok in ("[AI", "[TRANSCRIPT", "[WAITING")): return "ai_gate"
        return "info"

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(self._local, "emitting", False) or self._coordinator is None: return
        self._local.emitting = True
        try:
            msg = self.format(record)
            if msg: self._coordinator.emit_event("LOG", {"message": msg, "level": self._resolve_level(record, msg)})
        except Exception: pass
        finally: self._local.emitting = False


def classify_history_event(state_name: str, reason: Optional[str], data: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
    """Classify meaningful lifecycle transitions into HistoryView categories without polling spam."""
    st, r_raw = str(state_name or "").strip().upper(), str(reason or "").strip()
    r_low = r_raw.lower()
    if "SHUTDOWN" in st:
        if bool(data.get("is_demo")) or bool(data.get("dry_run")):
            return ("dry_run", "Simulation / Demo Shutdown Triggered", r_raw or str(data.get("target_action") or "Dry-run complete"))
        return ("power", "Power Action Dispatched", r_raw or str(data.get("target_action") or "Shutdown executed"))
    if bool(data.get("is_paused")) or "PAUS" in st: return ("snoozes", "Countdown Paused", r_raw or "User paused countdown")
    if r_low in _BLOCKER_TITLES: return ("blocker", _BLOCKER_TITLES[r_low], str(data.get("details") or r_raw))
    if r_low == "user_cancelled": return ("sessions", "Countdown Aborted by User", "user_cancelled")
    if r_low == "physical_interrupt": return ("sessions", "Physical Input Interrupt", "physical_interrupt")
    return None


def resolve_startup_mode(config: SettingsConfig, dry_run: bool) -> TargetMode:
    return TargetMode.SIMULATION if dry_run else MODE_STR_TO_ENUM.get(getattr(config, "execution_mode", "Live"), TargetMode.LIVE)


def resolve_initial_total_seconds(mode: TargetMode, config: SettingsConfig) -> int:
    return resolve_mode_duration_seconds(mode, config.master_shutdown_timer_min, getattr(config, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS))


def mode_to_settings_str(mode: TargetMode) -> str: return MODE_ENUM_TO_STR.get(mode, "Live")
def settings_str_to_mode(mode_str: str) -> TargetMode: return MODE_STR_TO_ENUM.get(mode_str, TargetMode.SIMULATION)


def sync_ai_snapshot(snapshot: Dict[str, Any], data: Optional[Dict[str, Any]]) -> None:
    if not data: return
    snapshot.update(data)
    if "subagent_count" in data and "workers" not in data: snapshot["workers"] = data["subagent_count"]
    elif "workers" in data and "subagent_count" not in data: snapshot["subagent_count"] = data["workers"]


def _read_has_user_input(coordinator: Any) -> bool:
    try:
        base = int(getattr(coordinator, "baseline_input_tick", 0) or 0)
        return bool(base and input_hook.get_last_input_tick() > base)
    except Exception:
        return False


def build_merged_context(coordinator: Any, snapshot: Dict[str, Any], extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {k: getattr(coordinator, k, d) for k, d in (("is_paused", False), ("bypass_inhibitors", False), ("target_mode", TargetMode.LIVE), ("ai_state", "READY"))}
    ctx.update(snapshot)
    if extra: ctx.update(extra)
    if ctx.get("idle_sec") is None and "user_inactivity_sec" in ctx: ctx["idle_sec"] = ctx["user_inactivity_sec"]
    if ctx.get("idle_threshold") is None and "inactivity_threshold_sec" in ctx: ctx["idle_threshold"] = ctx["inactivity_threshold_sec"]
    if "has_user_input" not in ctx: ctx["has_user_input"] = _read_has_user_input(coordinator)
    return ctx


def clear_stale_blocker_reasons(snapshot: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Clear stale inhibitor reason tokens when incoming telemetry shows blockers subsided."""
    reason = snapshot.get("reason")
    if reason == "process_tree_busy" and "is_tree_busy" in data and not data["is_tree_busy"]: snapshot["reason"] = None
    elif reason == "audio_active" and (("audio_active" in data and not data["audio_active"]) or ("audio_inhibit_enabled" in data and not data["audio_inhibit_enabled"])): snapshot["reason"] = None
    elif reason in ("hardware_busy", "cpu_busy", "network_busy") and ("cpu_percent" in data or "net_total_kb" in data):
        cpu, cpu_t = float(snapshot.get("cpu_percent", 0.0)), float(snapshot.get("cpu_threshold", 15.0))
        net, net_t = float(snapshot.get("net_total_kb", 0.0)), float(snapshot.get("net_threshold", 50.0))
        if cpu < cpu_t and not (net >= net_t and (net > 0.0 or net_t > 0.0)): snapshot["reason"] = None


def sync_windows_startup(cfg: SettingsConfig, logger: Any) -> None:
    reconcile_startup_shortcut(cfg, logger=logger, is_enabled_fn=is_startup_enabled, matches_fn=startup_matches_settings, enable_fn=enable_startup, disable_fn=disable_startup)


def sync_mini_hud_badges(app: Any, resolved: ResolvedPillState, hud_state: Optional[str] = None, ctx: Optional[Dict[str, Any]] = None) -> None:
    if not (app.mini_hud and app.mini_hud.winfo_exists()): return
    merged = ctx or app._merged_context()
    ai_key = resolve_ai_pill_state(merged, fallback_ai=getattr(app.coordinator, "ai_state", "READY"))
    mode_lbl = resolve_hud_mode_label(merged.get("target_mode", getattr(app.coordinator, "target_mode", None)), dry_run=app.dry_run)
    if hud_state == "DISARMED" or (app._hud_disarmed and resolved.pill_state in ("IDLE", "ACTIVE", "AWAY")):
        app.mini_hud.set_state("DISARMED", STATUS_GREEN); app.mini_hud.set_triple_status(ai_state=ai_key, sentinel_state=None, mode=mode_lbl)
    else:
        app.mini_hud.set_triple_status(ai_state=ai_key, sentinel_state=resolved.hud_badge, mode=mode_lbl)


def drain_coordinator_events(app: Any) -> None:
    handlers = {"TICK": app._handle_tick_event, "STATE_CHANGE": app._handle_state_change_event, "TELEMETRY": app._handle_telemetry_data_event, "LOG": app._handle_log_event, "AI_STATE_CHANGE": app._handle_ai_state_change_event, "MODE_CHANGE": app._handle_mode_change_event}
    pause_ts = getattr(app, "_pause_action_wall_ts", 0.0)
    while not app.coordinator.event_queue.empty():
        try:
            ev: TelemetryEvent = app.coordinator.event_queue.get_nowait()
            if ev.event_type in handlers:
                data = ev.data
                if pause_ts and ev.timestamp < pause_ts and ev.event_type in ("TICK", "TELEMETRY") and isinstance(data, dict):
                    data = {**data, "is_paused": bool(getattr(app.coordinator, "is_paused", False))}
                handlers[ev.event_type](data)
            elif ev.event_type == "CONFIG_UPDATED": app.terminal.append_log("Settings updated live in coordinator engine.", "success")
        except queue.Empty: break
        except Exception as exc: app.logger.error(f"[GUI] Error handling telemetry event: {exc}")


def _read_safe_idle_seconds(coordinator: Any) -> float:
    try: return round(float(coordinator._read_idle_seconds()), 1)
    except Exception: return 0.0


def apply_mode_change(app: Any, new_mode: TargetMode) -> None:
    app.dry_run = new_mode in (TargetMode.SIMULATION, TargetMode.DEMO_10S)
    app.coordinator.dry_run = app.dry_run; app.coordinator.set_target_mode(new_mode); app._hud_disarmed = True
    txt, bg = app.MODE_LABELS.get(new_mode, ("⚡ LIVE SHUTDOWN", "#EF4444"))
    app.chip_dryrun.config(text=f" {txt} ", bg=bg); app.title_bar.set_mode(new_mode)
    rem = app.coordinator.remaining_countdown_seconds; app.total_countdown_seconds = max(1, rem)
    st, eff_t, idle_s = app._coord_state_name(), int(app.coordinator.effective_user_inactivity_threshold()), _read_safe_idle_seconds(app.coordinator)
    mode_ctx = {"target_mode": new_mode.value, "state": st, "is_paused": False, "remaining": rem, "reason": None, "idle_sec": idle_s, "idle_threshold": eff_t, "inactivity_threshold_sec": eff_t, "has_user_input": False}
    app._last_telemetry_snapshot.update(mode_ctx); app._last_telemetry_snapshot.pop("is_tree_busy", None); app._last_telemetry_snapshot.pop("user_inactivity_sec", None)
    app.dashboard_view.update_health({**mode_ctx, "is_demo": new_mode in (TargetMode.DEMO_30S, TargetMode.DEMO_10S)})
    app.telemetry_view.update_telemetry(mode_ctx)
    app.update_countdown_display(rem, app.total_countdown_seconds, is_paused=False, idle_sec=idle_s, idle_threshold=eff_t); app._update_state_display(st, hud_state="DISARMED", context=mode_ctx)
    m_str = mode_to_settings_str(new_mode); app.config.execution_mode = m_str; app.settings_view.sync_mode_buttons(m_str)
    app.terminal.append_log("⚠️ DEMO (30s) ACTIVATED!" if new_mode == TargetMode.DEMO_30S else f"Mode switched: {new_mode.value}.", "crit" if new_mode == TargetMode.DEMO_30S else "info")


def apply_save_settings(app: Any, new_cfg: SettingsConfig) -> None:
    old_mode = getattr(app.config, "execution_mode", "Live")
    new_cfg.clamp(); app.config = new_cfg
    if not is_running_under_test(): save_settings_config(new_cfg)
    app.coordinator.update_config(new_cfg)
    if getattr(new_cfg, "execution_mode", "Live") != old_mode: apply_mode_change(app, settings_str_to_mode(new_cfg.execution_mode))
    else:
        app.total_countdown_seconds = resolve_initial_total_seconds(app.coordinator.target_mode, new_cfg)
        rem, eff_t = getattr(app.coordinator, "remaining_countdown_seconds", app.total_countdown_seconds), int(app.coordinator.effective_user_inactivity_threshold())
        app._last_telemetry_snapshot.update({"inactivity_threshold_sec": eff_t, "idle_threshold": eff_t, "cpu_threshold": new_cfg.cpu_threshold_pct, "net_threshold": new_cfg.network_threshold_kb})
        app.dashboard_view.update_health(app._merged_context({"remaining": rem})); app.update_countdown_display(rem, max(1, app.total_countdown_seconds))
    if not is_running_under_test(): sync_windows_startup(new_cfg, app.logger)
    app.terminal.append_log(f"Saved settings: Inact={new_cfg.user_inactivity_sec}s, Timer={new_cfg.master_shutdown_timer_min}m", "success")


def handle_pause_toggle_action(app: Any) -> None:
    """Toggle coordinator pause/resume immediately on first click and sync all UI surfaces."""
    app._hud_disarmed = False
    is_p = not bool(getattr(app.coordinator, "is_paused", False))
    app.coordinator.pause_countdown() if is_p else app.coordinator.resume_countdown()
    app._pause_action_wall_ts = time.time()
    app.terminal.append_log("Countdown paused." if is_p else "Countdown resumed.", "warn" if is_p else "info")
    st = app._coord_state_name()
    if hasattr(app, "_sync_idle_snap"): idle_s, idle_t, snap = app._sync_idle_snap(st, is_paused=is_p)
    else: app._last_telemetry_snapshot.update({"state": st, "is_paused": is_p}); snap = app._last_telemetry_snapshot; idle_s, idle_t = snap.get("idle_sec"), snap.get("idle_threshold")
    app._update_state_display(st, context=snap); rem = getattr(app.coordinator, "remaining_countdown_seconds", app.total_countdown_seconds)
    app.update_countdown_display(rem, max(1, app.total_countdown_seconds), is_paused=is_p, idle_sec=idle_s, idle_threshold=idle_t)
    app.dashboard_view.set_pause_state(is_p)
    if app.mini_hud and app.mini_hud.winfo_exists(): app.mini_hud.is_paused = is_p; app.mini_hud.btn_pause.config(text="▶" if is_p else "⏸")


def handle_snooze_action(app: Any, seconds: int = 300) -> None:
    """Apply snooze duration, preserve dual timers, refresh grace pill, and record history."""
    new_rem = app.coordinator.snooze_countdown(seconds)
    app.total_countdown_seconds = max(app.total_countdown_seconds, new_rem)
    st = app._coord_state_name()
    app._last_telemetry_snapshot.update({"state": st, "remaining": new_rem, "total_seconds": app.total_countdown_seconds})
    app.dashboard_view.update_health(app._merged_context({"remaining": new_rem, "state": st}))
    app.update_countdown_display(new_rem, max(1, app.total_countdown_seconds))
    app._update_state_display(st)
    app.terminal.append_log(f"Snooze activated (+{seconds // 60}m). Remaining: {new_rem}s.", "info")
    app.history_view.add_event("snoozes", "User Snooze Activated", "Just now", f"+{seconds // 60} minutes")


def toggle_mini_hud_visibility(app: Any) -> None:
    """Show, restore, or hide the floating Mini HUD from tray menu without losing idle state."""
    if not (app.mini_hud and app.mini_hud.winfo_exists()): app._toggle_mini_hud(); return
    if app.mini_hud.wm_state() != "withdrawn":
        app.mini_hud.withdraw(); app.terminal.append_log("Floating Mini-HUD hidden.", "info"); return
    ctx = app._merged_context()
    app.mini_hud.restore_hud(idle_sec=ctx.get("idle_sec"), idle_threshold=ctx.get("idle_threshold", ctx.get("inactivity_threshold_sec")))


def _safe_ignore(fn: Any, *args: Any) -> None:
    try: fn(*args)
    except Exception: pass


def dock_app_to_tray(app: Any) -> None:
    """Dock to system tray, or safely fall back to Mini HUD / taskbar minimize if tray is unavailable."""
    if app.tray_icon is None:
        app.logger.warning("System tray unavailable (pystray missing); opening Mini HUD / minimizing to taskbar instead of hiding completely.")
        app.terminal.append_log("System tray unavailable; opening Mini HUD / taskbar minimize instead.", "warn")
        _safe_ignore(lambda: (app.withdraw(), None if (app.mini_hud and app.mini_hud.winfo_exists()) else app._toggle_mini_hud()))
        if not (app.mini_hud and app.mini_hud.winfo_exists()): app.deiconify(); app.iconify()
        return
    if app.mini_hud and app.mini_hud.winfo_exists(): app.mini_hud.withdraw()
    app.withdraw(); app.terminal.append_log("Smart Shutdown docked in system tray.", "info")


def cleanup_app_runtime(app: Any) -> None:
    """Cancel scheduled event timer, detach log handler, stop tray, Mini HUD, and coordinator."""
    app._is_running = False
    for attr, fn in (("_event_after_id", app.after_cancel), ("tray_icon", stop_tray_icon)):
        obj = getattr(app, attr, None)
        if obj: setattr(app, attr, None); _safe_ignore(fn, obj)
    handler = getattr(app, "_log_handler", None)
    if handler is not None and getattr(app, "logger", None) is not None:
        app._log_handler = None; _safe_ignore(app.logger.removeHandler, handler)
    if getattr(app, "mini_hud", None) and app.mini_hud.winfo_exists():
        _safe_ignore(app.mini_hud.destroy); app.mini_hud = None
    if getattr(app, "coordinator", None) is not None:
        _safe_ignore(app.coordinator.stop_background_loop, 1.0)
