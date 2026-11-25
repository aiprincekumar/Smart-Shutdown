# -*- coding: utf-8 -*-
"""
gui.components.status_resolver: Pure-Python dynamic status pill and badge resolution engine.
Zero tkinter imports. Rule 28 Modularity Compliant (< 150 lines).
Department 02 Solution Architecture / Department 05 Frontend & Desktop Engineering.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from core.models import TargetMode
from gui.theme import (
    ACCENT_CYAN, ACCENT_PURPLE, STATUS_AMBER,
    STATUS_EMERALD, STATUS_GREEN, STATUS_ORANGE, STATUS_RED,
)


@dataclass(frozen=True)
class ResolvedPillState:
    """Resolved visual status metadata synchronized across TitleBar, MiniHUD, and pill."""
    pill_state: str
    hud_badge: str
    color: str
    title_bar_state: str


_PILL_CLOSING = ResolvedPillState("CLOSING", "Closing", STATUS_ORANGE, "CLOSING")
_PILL_PAUSED = ResolvedPillState("PAUSED", "Paused", STATUS_AMBER, "PAUSED")
_PILL_SHUTDOWN = ResolvedPillState("SHUTDOWN", "Shutdown", STATUS_RED, "SHUTDOWN")
_PILL_BLOCKED = ResolvedPillState("BLOCKED", "Blocked", STATUS_RED, "BLOCKED")
_PILL_WAITING = ResolvedPillState("WAITING_USER_PROMPT", "Waiting", ACCENT_PURPLE, "WAITING_USER_PROMPT")
_PILL_EVAL = ResolvedPillState("AI_EVALUATION", "Eval", ACCENT_CYAN, "AI_EVALUATION")
_PILL_RUNNING = ResolvedPillState("RUNNING", "Running", STATUS_EMERALD, "RUNNING")
_PILL_ACTIVE = ResolvedPillState("ACTIVE", "Active", STATUS_EMERALD, "ACTIVE")
_PILL_AWAY = ResolvedPillState("AWAY", "Away", STATUS_EMERALD, "AWAY")
_PILL_IDLE = ResolvedPillState("IDLE", "Idle", STATUS_GREEN, "IDLE")


def _to_float(val: Any) -> Optional[float]:
    """Safely convert numeric value to float, returning None if missing or invalid."""
    if val is None: return None
    try: return float(val)
    except (TypeError, ValueError): return None


def _extract_idle_seconds(ctx: Dict[str, Any]) -> Optional[float]:
    """Safely parse idle_sec or user_inactivity_sec from context as float."""
    raw = ctx.get("idle_sec")
    return _to_float(ctx.get("user_inactivity_sec") if raw is None else raw)


def _has_token(text: str, tokens: Tuple[str, ...]) -> bool:
    """Return True if any token substring appears in text."""
    return any(tok in text for tok in tokens)


def _resolve_priority_pill(s: str, ctx: Dict[str, Any]) -> Optional[ResolvedPillState]:
    """Resolve high-precedence lifecycle states (closing, shutdown, paused, blocked, eval)."""
    is_paused = bool(ctx.get("is_paused", False))
    if _has_token(s, ("CLOSING", "GRACE", "CLOSE")): return _PILL_PAUSED if is_paused else _PILL_CLOSING
    if "SHUTDOWN" in s: return _PILL_SHUTDOWN
    if is_paused or "PAUS" in s: return _PILL_PAUSED
    bypass = bool(ctx.get("bypass_inhibitors", False))
    audio_blocked = bool(ctx.get("audio_active", False)) and bool(ctx.get("audio_inhibit_enabled", True))
    hw_or_tree_blocked = (not bypass) and (
        ctx.get("reason") in ("process_tree_busy", "audio_active", "hardware_busy", "cpu_busy", "network_busy")
        or bool(ctx.get("is_tree_busy", False)) or audio_blocked
    )
    if "BLOCK" in s or ("AI_EVAL" in s and hw_or_tree_blocked): return _PILL_BLOCKED
    if _has_token(s, ("WAITING_USER", "PROMPT")): return _PILL_WAITING
    if "AI_EVAL" in s: return _PILL_EVAL
    return None


def resolve_sentinel_pill_state(state_name: str, context: Optional[Dict[str, Any]] = None) -> ResolvedPillState:
    """Resolve authoritative lifecycle pill state, Mini HUD badge, and color via strict precedence."""
    ctx, s = context or {}, str(state_name or "").strip().upper()
    priority = _resolve_priority_pill(s, ctx)
    if priority is not None: return priority
    if _has_token(s, ("COUNTDOWN", "RUN")): return _PILL_RUNNING
    if s == "AWAY": return _PILL_AWAY
    if s == "ACTIVE": return _PILL_ACTIVE
    if s in ("IDLE_MONITORING", "ABORTED_RESET", ""):
        idle_s, has_input = _extract_idle_seconds(ctx), ctx.get("has_user_input")
        if idle_s is not None and idle_s >= 5.0: return _PILL_AWAY
        if has_input is not False and idle_s is not None and idle_s < 5.0: return _PILL_ACTIVE
    return _PILL_IDLE


def resolve_presence_phase(state_name: Optional[str] = None, idle_sec: Optional[float] = None, idle_threshold: Optional[float] = None, has_user_input: Optional[bool] = None) -> str:
    """Return unified presence phase ('AWAY', 'ACTIVE', or 'IDLE')."""
    s = str(state_name or "").strip().upper()
    if _has_token(s, ("COUNTDOWN", "RUN", "AWAY", "CLOSING", "GRACE")): return "AWAY"
    idle_val, thresh_val = _to_float(idle_sec), _to_float(idle_threshold)
    if s == "ACTIVE": return "ACTIVE"
    if idle_val is not None:
        if (thresh_val is not None and thresh_val > 0 and idle_val >= thresh_val) or idle_val >= 5.0: return "AWAY"
        if has_user_input is not False and idle_val < 5.0: return "ACTIVE"
    return "IDLE"


def resolve_input_card_status(idle_sec: Optional[float] = None, idle_threshold: Optional[float] = None, audio_active: bool = False, state_name: Optional[str] = None, has_user_input: Optional[bool] = None) -> str:
    """Resolve Telemetry Input & Audio card status ('AUDIO', 'AWAY', 'ACTIVE', or 'IDLE')."""
    phase = resolve_presence_phase(state_name, idle_sec, idle_threshold, has_user_input=has_user_input)
    return ("AUDIO" if bool(audio_active) else "AWAY") if phase == "AWAY" else phase


def resolve_input_activity_state(state_name: Optional[str] = None, idle_sec: Optional[float] = 0.0, idle_threshold: Optional[float] = 60.0, audio_active: bool = False, has_user_input: Optional[bool] = None) -> str:
    """SSOT helper resolving unified input activity status ('ACTIVE', 'IDLE', 'AWAY', or 'AUDIO')."""
    return resolve_input_card_status(idle_sec=idle_sec, idle_threshold=idle_threshold, audio_active=audio_active, state_name=state_name, has_user_input=has_user_input)


def resolve_ai_pill_state(data: Dict[str, Any], fallback_ai: str = "READY") -> str:
    """Resolve canonical AI engine badge key from coordinator state and worker counts."""
    raw_ai = data.get("ai_state", fallback_ai)
    ai_st = str(fallback_ai if raw_ai is None else raw_ai).strip().upper()
    raw_workers = data.get("subagent_count", data.get("workers", data.get("worker_count", 0)))
    try:
        workers = int(0 if raw_workers is None else raw_workers)
    except (TypeError, ValueError):
        workers = 0

    if "WAITING" in ai_st or "INPUT" in ai_st:
        return "WAITING"
    if "BUSY" in ai_st and workers == 0:
        return "BUSY"
    if "WORK" in ai_st or "BUSY" in ai_st or workers > 0:
        return "WORKING"
    return "READY"


def resolve_mode_enum(raw_mode: Any) -> TargetMode:
    """Normalize a raw enum, mode name, or UI label string into TargetMode."""
    if isinstance(raw_mode, TargetMode):
        return raw_mode
    s = str(raw_mode or "").strip().upper()
    if "30" in s:
        return TargetMode.DEMO_30S
    if "10" in s:
        return TargetMode.DEMO_10S
    if "DEMO" in s:
        return TargetMode.DEMO_30S
    if "SIM" in s or "DRY" in s:
        return TargetMode.SIMULATION
    return TargetMode.LIVE


def resolve_hud_mode_label(mode: Any, dry_run: bool = False) -> str:
    """Resolve concise Mini HUD mode label ('Demo', 'Sim', or 'Live') from TargetMode."""
    if mode is not None:
        resolved = resolve_mode_enum(mode)
        if resolved in (TargetMode.DEMO_30S, TargetMode.DEMO_10S):
            return "Demo"
        if resolved == TargetMode.SIMULATION:
            return "Sim"
        return "Live"
    return "Sim" if dry_run else "Live"


def extract_timer_snapshot(
    data: Dict[str, Any], fallback_rem: int = 0, fallback_paused: bool = False
) -> Tuple[int, bool, Optional[float], Optional[float]]:
    """Extract normalized (remaining_sec, is_paused, idle_sec, idle_threshold) from payload."""
    raw_rem = data.get("remaining", fallback_rem)
    rem = int(fallback_rem if raw_rem is None else raw_rem)
    paused = bool(data.get("is_paused", fallback_paused))
    idle_s = _extract_idle_seconds(data)
    thresh_s = _to_float(data.get("idle_threshold", data.get("inactivity_threshold_sec")))
    return rem, paused, idle_s, thresh_s


__all__ = [
    "ResolvedPillState",
    "resolve_sentinel_pill_state",
    "resolve_presence_phase",
    "resolve_input_card_status",
    "resolve_input_activity_state",
    "resolve_ai_pill_state",
    "resolve_mode_enum",
    "resolve_hud_mode_label",
    "extract_timer_snapshot",
]
