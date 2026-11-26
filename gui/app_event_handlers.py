# -*- coding: utf-8 -*-
"""
gui.app_event_handlers: Coordinator event-handler logic and state sync helpers.
Extracted from gui.unified_app per Universal Rule 28 (< 140 lines, < 8 KB).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from typing import Any, Dict, Optional

from gui.app_event_bridge import _read_safe_idle_seconds, classify_history_event, clear_stale_blocker_reasons, sync_mini_hud_badges
from gui.components.status_resolver import resolve_hud_mode_label, resolve_mode_enum, resolve_sentinel_pill_state


def build_state_change_health_payload(data: Dict[str, Any], reason: Optional[str]) -> Dict[str, Any]:
    """Copy state-change event payload and normalize Process Tree busy flag for DashboardView."""
    out = dict(data)
    if "is_tree_busy" not in data:
        out["is_tree_busy"] = (reason == "process_tree_busy")
    return out


def sync_idle_snap(app: Any, st: str, idle_s: Optional[float] = None, extra: Optional[Dict[str, Any]] = None) -> tuple:
    """Build synchronized idle snapshot including config.audio_inhibit_enabled."""
    fn = getattr(app.coordinator, "effective_user_inactivity_threshold", None)
    idle_t = int(fn() if fn else getattr(app.config, "user_inactivity_sec", 60))
    s = _read_safe_idle_seconds(app.coordinator) if idle_s is None else idle_s
    snap: Dict[str, Any] = {
        "state": st, "idle_sec": s, "idle_threshold": idle_t, "inactivity_threshold_sec": idle_t,
        "has_user_input": False, "audio_inhibit_enabled": bool(getattr(app.config, "audio_inhibit_enabled", True)),
    }
    if extra:
        snap.update(extra)
    app._last_telemetry_snapshot.update(snap)
    app.dashboard_view._last_telemetry["has_user_input"] = snap["has_user_input"]
    return s, idle_t, snap


def handle_mode_change_event(app: Any, data: Dict[str, Any]) -> None:
    """Apply coordinator MODE_CHANGE event across title bar, Mini HUD, and DashboardView."""
    try:
        mode_enum = resolve_mode_enum(data.get("mode", data.get("target_mode", "")))
        app._last_telemetry_snapshot["target_mode"] = mode_enum.value
        if app.title_bar.current_mode != mode_enum:
            app.title_bar.set_mode(mode_enum)
        if app.mini_hud and app.mini_hud.winfo_exists():
            app.mini_hud.set_triple_status(mode=resolve_hud_mode_label(mode_enum, dry_run=app.dry_run))
        app.dashboard_view.update_health(data)
    except Exception as exc:
        app.logger.error(f"[GUI] Error handling mode change event: {exc}")


def handle_tick_event(app: Any, data: Dict[str, Any]) -> None:
    """Apply coordinator TICK event to timer display, telemetry snapshot, and status pills."""
    st = data.get("state") or app._coord_state_name()
    app.dashboard_view._last_telemetry["state"] = st
    is_p = app._apply_timer_payload(data)
    app._last_telemetry_snapshot.update({k: v for k, v in data.items() if k != "reason"})
    app._last_telemetry_snapshot["is_paused"] = is_p
    if st in app._ARMING_STATES:
        app._hud_disarmed = False
    app._update_state_display(st, context=app._merged_context(data))


def handle_state_change_event(app: Any, data: Dict[str, Any]) -> None:
    """Apply coordinator STATE_CHANGE event and forward normalized health payload."""
    st, reason = data.get("state", "UNKNOWN"), data.get("reason")
    if reason == "user_cancelled":
        app._hud_disarmed = True
    elif st in app._ARMING_STATES:
        app._hud_disarmed = False
    app._last_telemetry_snapshot.update(data)
    app._last_telemetry_snapshot["reason"] = reason
    if "is_tree_busy" not in data and reason != "process_tree_busy":
        app._last_telemetry_snapshot.pop("is_tree_busy", None)
    hud_state = "DISARMED" if reason == "user_cancelled" else None
    app._update_state_display(st, hud_state=hud_state, context=app._merged_context(data))
    app.terminal.append_log(f"Coordinator state: {st} (data: {data})", "info")
    app.dashboard_view.update_health(build_state_change_health_payload(data, reason))
    if any(k in data for k in app._TIMER_KEYS):
        app._apply_timer_payload(data)
    classified = classify_history_event(st, reason, data)
    if classified is not None:
        app.history_view.add_event(classified[0], classified[1], "Just now", classified[2])


def handle_telemetry_data_event(app: Any, data: Dict[str, Any]) -> None:
    """Apply coordinator TELEMETRY event to telemetry deck, dashboard cards, and state pills."""
    app._last_telemetry_snapshot.update(data)
    clear_stale_blocker_reasons(app._last_telemetry_snapshot, data)
    if data.get("state") in app._ARMING_STATES:
        app._hud_disarmed = False
    app.telemetry_view.update_telemetry(data)
    app.dashboard_view.update_health(data)
    app._update_title_bar_ai(data)
    state_name = data.get("state") or app._last_telemetry_snapshot.get("state") or app._coord_state_name()
    app._update_state_display(state_name, context=app._merged_context())
    if any(k in data for k in app._TIMER_KEYS):
        app._apply_timer_payload(data)


def update_state_display(
    app: Any, state_name: str, hud_state: Optional[str] = None, context: Optional[Dict[str, Any]] = None
) -> None:
    """Synchronize TitleBar, status pill, Mini HUD badges, and Tab 2 telemetry state."""
    app.dashboard_view._last_telemetry["state"] = state_name
    ctx = app._merged_context(context)
    app.dashboard_view._last_telemetry["has_user_input"] = ctx.get("has_user_input")
    resolved = resolve_sentinel_pill_state(state_name, ctx)
    app.title_bar.set_sentinel_state(resolved.title_bar_state)
    app.pill_status.config(text=f" {resolved.pill_state} ", bg=resolved.color)
    sync_mini_hud_badges(app, resolved, hud_state=hud_state, ctx=ctx)
    if hasattr(app, "telemetry_view"):
        tv_ctx = {k: ctx[k] for k in app._TV_SYNC_KEYS if k in ctx}
        tv_ctx["state"] = state_name
        app.telemetry_view.update_telemetry(tv_ctx)


__all__ = [
    "build_state_change_health_payload",
    "sync_idle_snap",
    "handle_mode_change_event",
    "handle_tick_event",
    "handle_state_change_event",
    "handle_telemetry_data_event",
    "update_state_display",
]
