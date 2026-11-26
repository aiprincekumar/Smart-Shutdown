# -*- coding: utf-8 -*-
"""
core.coordinator_helpers: Stateless payload builders, gate evaluators, and power-flush helpers.
Extracted from core.coordinator per Universal Rule 28 (< 140 lines, < 8 KB).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from typing import Any, Dict, Optional, Union

from core.models import AntiGravityAIState, LifecycleState, TargetMode
from core.telemetry_collector import normalize_telemetry_defaults


def resolve_target_mode(mode: Union[TargetMode, str]) -> TargetMode:
    """Normalize enum or string mode descriptor to TargetMode."""
    if isinstance(mode, TargetMode):
        return mode
    m = str(mode).upper()
    for token, target in (("30", TargetMode.DEMO_30S), ("10", TargetMode.DEMO_10S), ("DEMO", TargetMode.DEMO_30S)):
        if token in m:
            return target
    return TargetMode.SIMULATION if ("SIM" in m or "DRY" in m) else TargetMode.LIVE


def read_idle_seconds(hook_mod: Any) -> float:
    """Safely read physical user inactivity seconds from input hook module."""
    try:
        return float(getattr(hook_mod, "get_user_idle_seconds", hook_mod.get_idle_seconds)())
    except Exception:
        return 0.0


def build_state_payload(coord: Any, hook_mod: Any, extra: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble standardized coordinator state event payload merged with extra overrides."""
    eff_thresh = int(coord.effective_user_inactivity_threshold())
    idle_sec = coord._read_idle_seconds()
    p = {
        "state": coord.state.value if isinstance(coord.state, LifecycleState) else str(coord.state),
        "target_mode": coord.target_mode.value,
        "mode": coord.target_mode.value,
        "is_demo": coord.target_mode in (TargetMode.DEMO_30S, TargetMode.DEMO_10S),
        "is_paused": coord.is_paused,
        "active_count": coord._last_active_count,
        "subagent_count": coord._last_subagent_count,
        "workers": coord._last_subagent_count,
        "dry_run": coord.dry_run,
        "idle_sec": round(idle_sec, 1),
        "has_user_input": bool(coord.baseline_input_tick and hook_mod.get_last_input_tick() > coord.baseline_input_tick),
        "idle_threshold": eff_thresh,
        "inactivity_threshold_sec": eff_thresh,
        "idle_remaining_sec": max(0, eff_thresh - int(idle_sec)),
        "idle_pct": round(max(0.0, min(1.0, idle_sec / max(1, eff_thresh))), 3),
        "remaining": coord.remaining_countdown_seconds,
        "remaining_seconds": coord.remaining_countdown_seconds,
        "total_seconds": coord._default_mode_seconds(),
        "target_action": getattr(coord.config, "target_action", "Shutdown"),
    }
    p.update(extra)
    return p


def build_telemetry_payload(coord: Any, hw: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build normalized TELEMETRY event payload synchronized with SettingsConfig."""
    raw = hw if hw is not None else coord._last_hw_telemetry
    hw_data = normalize_telemetry_defaults(raw, coord.config)
    return coord._state_payload(
        **hw_data,
        is_paused=coord.is_paused,
        waiting_mode=coord.config.waiting_mode,
        bypass_inhibitors=coord.bypass_inhibitors,
        ai_state=coord.ai_state,
    )


def evaluate_waiting_gates(coord: Any, eval_res: Dict[str, Any], gate_mod: Any) -> Optional[Dict[str, Any]]:
    """Evaluate interactive prompt waiting gates across active AI sessions."""
    mode = coord._get_waiting_mode_enum()
    hybrid_timeout = float(coord.config.waiting_hybrid_timeout_min * 60)
    for session in eval_res.get("sessions", []):
        if session.get("status") != "WAITING_USER":
            continue
        gate_res = gate_mod.evaluate_waiting_state(session_state=session, mode=mode, timeout_seconds=hybrid_timeout)
        if gate_res.should_block_shutdown:
            coord.state, coord.ai_state = LifecycleState.WAITING_USER_PROMPT, AntiGravityAIState.INPUT_PENDING.value
            coord.logger.info(f"[COORDINATOR] Waiting user prompt: {gate_res.details}")
            coord._emit_state(reason="waiting_user_input", details=gate_res.details)
            coord._emit_ai(details=gate_res.details)
            return {"status": "WAITING_USER_BLOCKED", "gate_res": gate_res, "eval_res": eval_res}
    return None


def evaluate_system_blockers(
    coord: Any, eval_res: Dict[str, Any], tree_mod: Any, hw_eval_fn: Any
) -> Optional[Dict[str, Any]]:
    """Evaluate process tree, active transcripts, and hardware/audio inhibitors."""
    if coord.bypass_inhibitors:
        return None
    if tree_mod.is_process_tree_busy():
        coord.state = LifecycleState.AI_EVALUATION
        coord._emit_state(reason="process_tree_busy", is_tree_busy=True)
        return {"status": "AI_BUSY_PROCESS", "eval_res": eval_res}
    if eval_res.get("active_count", 0) > 0:
        coord.state, coord.ai_state = LifecycleState.AI_EVALUATION, AntiGravityAIState.WORKING.value
        coord._emit_ai(reason="transcripts_active", active_count=coord._last_active_count, subagent_count=coord._last_subagent_count)
        return {"status": "AI_BUSY_TRANSCRIPT", "eval_res": eval_res}
    hw_reason = hw_eval_fn(coord._last_hw_telemetry, coord.config)
    if hw_reason:
        coord.state = LifecycleState.AI_EVALUATION
        coord.logger.info(f"[COORDINATOR] Inhibited by {hw_reason}.")
        coord._emit_state(reason=hw_reason)
        return {"status": "HW_BUSY_INHIBITED", "reason": hw_reason, "eval_res": eval_res}
    return None


def flush_before_power_action(coord: Any, release_lock_fn: Any) -> None:
    """Flush log handlers and release single-instance lock prior to OS power action."""
    if coord.dry_run:
        return
    for handler in list(getattr(coord.logger, "handlers", [])):
        try:
            handler.flush()
        except Exception:
            pass
    try:
        release_lock_fn(logger=coord.logger)
    except Exception:
        pass


__all__ = [
    "resolve_target_mode", "read_idle_seconds", "build_state_payload",
    "build_telemetry_payload", "evaluate_waiting_gates", "evaluate_system_blockers", "flush_before_power_action",
]
