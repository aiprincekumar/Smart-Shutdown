# -*- coding: utf-8 -*-
"""
gui.components.health_summary: Pure presentation-model specs and card formatters
for DashboardView's 6 floating health cards (zero tkinter imports).
Department 05 Frontend & Desktop Engineering / Rule 28 Modularity Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from gui.theme import (
    ACCENT_CYAN,
    ACCENT_PURPLE,
    STATUS_AMBER,
    STATUS_EMERALD,
    STATUS_SLATE,
)


@dataclass(frozen=True)
class HealthCardSpec:
    """Immutable specification for one Dashboard floating health card."""

    key: str
    label: str
    default_chip: str
    default_color: str
    is_switch: bool = False


HEALTH_CARD_SPECS: Tuple[HealthCardSpec, ...] = (
    HealthCardSpec("cpu", "CPU Activity", "0.0% [Safe]", STATUS_EMERALD, False),
    HealthCardSpec("net", "Network Transfer", "0.0 KB/s [Idle]", STATUS_EMERALD, False),
    HealthCardSpec("ai", "Antigravity Task", "[ ✨ Ready ] All Done", STATUS_EMERALD, True),
    HealthCardSpec("audio", "Audio Stream", "[ 🔇 Silent ]", STATUS_EMERALD, True),
    HealthCardSpec("tree", "Process Tree", "Idle", STATUS_EMERALD, True),
    HealthCardSpec("inactivity", "User Inactivity", "0s [Threshold: 60s]", STATUS_AMBER, False),
)


def _to_nonneg_int(val: Any, default: int = 0) -> int:
    """Safely convert numeric input to a non-negative integer."""
    if val is None or isinstance(val, bool):
        return max(0, default)
    try:
        return max(0, int(val))
    except (TypeError, ValueError):
        try:
            return max(0, int(float(val)))
        except (TypeError, ValueError):
            return max(0, default)


def _to_float(val: Any, default: float = 0.0) -> float:
    """Safely convert numeric input to float."""
    if val is None or isinstance(val, bool):
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _pick(data: Dict[str, Any], primary: str, fallback: str) -> Any:
    """Return primary key value when present and non-None, else fallback key value."""
    val = data.get(primary)
    return data.get(fallback) if val is None else val


def _resolve_tree_workers(data: Dict[str, Any]) -> int:
    """Resolve Process Tree worker count strictly decoupled from AI subagent_count."""
    raw_workers = data.get("worker_count")
    if raw_workers is None and isinstance(data.get("active_pids"), (list, tuple, set)):
        raw_workers = len(data["active_pids"])
    return _to_nonneg_int(raw_workers, 0)


def format_cpu_card(data: Dict[str, Any]) -> Tuple[str, str, float, bool]:
    """Format CPU Activity chip text, color, fill ratio, and safe flag."""
    cpu = max(0.0, _to_float(_pick(data, "cpu_percent", "cpu_pct"), 0.0))
    thresh = _to_float(data.get("cpu_threshold"), 15.0)
    cpu_safe = cpu < thresh
    color = STATUS_EMERALD if cpu_safe else STATUS_AMBER
    text = f"{cpu:.1f}% [Safe]" if cpu_safe else f"{cpu:.1f}% [Spike]"
    return text, color, cpu / 100.0, cpu_safe


def format_net_card(data: Dict[str, Any]) -> Tuple[str, str, float, bool]:
    """Format Network Transfer chip text, color, fill ratio, and idle flag."""
    net = max(0.0, _to_float(_pick(data, "net_total_kb", "net_kb_s"), 0.0))
    thresh = _to_float(data.get("net_threshold"), 50.0)
    net_idle = (net < thresh) if thresh > 0.0 else (net <= 0.0)
    color = STATUS_EMERALD if net_idle else STATUS_AMBER
    text = f"{net:.1f} KB/s [Idle]" if net_idle else f"{net:.1f} KB/s [Busy]"
    return text, color, net / max(thresh * 2.0, 50.0), net_idle


def format_ai_card(data: Dict[str, Any]) -> Tuple[str, str, bool, str]:
    """Format Antigravity Task chip text, color, switch state, and uppercase AI state."""
    ai_st = str(data.get("ai_state", "READY") or "READY").upper()
    workers = _to_nonneg_int(_pick(data, "subagent_count", "workers"), 0)
    if "WAITING" in ai_st or "INPUT" in ai_st:
        return "[ 💬 Waiting ] Pending", ACCENT_PURPLE, False, ai_st
    if workers > 0:
        return f"Active AI Work ({workers} Active)", ACCENT_CYAN, True, ai_st
    if "WORK" in ai_st or "BUSY" in ai_st:
        return "[ ⚙️ Working ] Background Tasks", STATUS_AMBER, True, ai_st
    return "[ ✨ Ready ] All Done", STATUS_EMERALD, False, ai_st


def ai_pill_color(chip_color: str, dot_active: bool) -> str:
    """Resolve status pill dot color matching historical Antigravity Task visuals."""
    if chip_color == ACCENT_CYAN:
        return STATUS_EMERALD
    if not dot_active and chip_color == STATUS_EMERALD:
        return STATUS_SLATE
    return chip_color


def format_audio_card(data: Dict[str, Any]) -> Tuple[str, str, bool]:
    """Format Audio Stream chip text, color, and active dot state."""
    if not bool(data.get("audio_inhibit_enabled", True)):
        return "[ Disabled ]", STATUS_SLATE, False
    if bool(data.get("audio_active", False)):
        return "[ 🔊 Playing ]", STATUS_AMBER, True
    return "[ 🔇 Silent ]", STATUS_EMERALD, False


def format_process_tree_card(data: Dict[str, Any]) -> Tuple[str, str, bool]:
    """Format Process Tree chip text, color, and busy dot state."""
    workers = _resolve_tree_workers(data)
    memory_mb = _to_nonneg_int(data.get("memory_mb"), 0)
    busy = bool(data.get("is_tree_busy", False)) or (workers > 0)
    if busy and workers > 0:
        unit = "worker" if workers == 1 else "workers"
        cand = f"Busy ({workers} {unit} / {memory_mb} MB)"
        text = cand if len(cand) <= 26 else f"Busy ({workers}W / {memory_mb} MB)"
        return text, STATUS_AMBER, True
    if busy:
        text = f"Busy ({memory_mb} MB)" if memory_mb > 0 else "Busy [Active]"
        return text, STATUS_AMBER, True
    text = f"Idle ({memory_mb} MB)" if memory_mb > 0 else "Idle"
    return text, STATUS_EMERALD, False


def format_inactivity_card(data: Dict[str, Any]) -> Tuple[str, str, float]:
    """Format User Inactivity chip text, color, and normalized threshold ratio."""
    idle_s = _to_nonneg_int(_pick(data, "idle_sec", "user_inactivity_sec"), 0)
    raw_thresh = _pick(data, "inactivity_threshold_sec", "idle_threshold")
    thresh_s = _to_nonneg_int(raw_thresh, 60) if raw_thresh is not None else 60
    color = STATUS_EMERALD if idle_s >= thresh_s else STATUS_AMBER
    if thresh_s <= 60:
        text = f"{idle_s}s [Threshold: {thresh_s}s]"
    elif thresh_s % 60 == 0 and idle_s % 60 == 0:
        text = f"{idle_s // 60} mins [Threshold: {thresh_s // 60} mins]"
    else:
        text = f"{idle_s // 60}m {idle_s % 60}s [Threshold: {thresh_s // 60}m]"
    return text, color, idle_s / max(thresh_s, 1)


def format_health_tooltip(data: Dict[str, Any]) -> str:
    """Format hover summary including Audio Stream and Process Tree descriptors."""
    if not data:
        return ""
    cpu = _to_float(_pick(data, "cpu_percent", "cpu_pct"), 0.0)
    net = _to_float(_pick(data, "net_total_kb", "net_kb_s"), 0.0)
    idle = _to_nonneg_int(data.get("idle_sec"), 0)
    mode = data.get("target_mode", "LIVE")
    state = data.get("state", "IDLE_MONITORING")
    workers = _to_nonneg_int(_pick(data, "subagent_count", "workers"), 0)
    audio_txt = format_audio_card(data)[0]
    audio_lbl = "Off" if "Disabled" in audio_txt else ("Playing" if "Playing" in audio_txt else "Silent")
    tw = _resolve_tree_workers(data)
    mem = _to_nonneg_int(data.get("memory_mb"), 0)
    busy = bool(data.get("is_tree_busy", False)) or tw > 0
    tree_lbl = f"Busy {tw}W ({mem} MB)" if busy else f"{tw}W ({mem} MB)"
    return (
        f"[{mode}] State: {state} | CPU: {cpu:.1f}% | Net: {net:.1f} KB/s | "
        f"Idle: {idle}s | Workers: {workers} | Audio: {audio_lbl} | Tree: {tree_lbl}"
    )


def _sync_ai_worker_keys(store: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    """Synchronize subagent_count and workers aliases for Antigravity Task."""
    if "subagent_count" in incoming and "workers" not in incoming:
        store["workers"] = incoming["subagent_count"]
    elif "workers" in incoming and "subagent_count" not in incoming:
        store["subagent_count"] = incoming["workers"]


def _apply_tree_state(store: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    """Handle explicit Process Tree resets and process_tree_busy state inference."""
    if "is_tree_busy" in incoming and not incoming["is_tree_busy"]:
        if "worker_count" not in incoming:
            store["worker_count"] = 0
        if "active_pids" not in incoming and "worker_count" not in incoming:
            store["active_pids"] = []
    if incoming.get("reason") == "process_tree_busy" and "is_tree_busy" not in incoming:
        store["is_tree_busy"] = True


def _apply_audio_reset(store: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    """Clear stale audio_active when audio_inhibit_enabled is explicitly disabled."""
    if "audio_inhibit_enabled" in incoming and not incoming["audio_inhibit_enabled"]:
        if "audio_active" not in incoming:
            store["audio_active"] = False


def merge_health_telemetry(store: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    """Merge partial telemetry into store while synchronizing aliases and explicit resets."""
    if not incoming:
        return
    if "state" in incoming and "reason" not in incoming:
        store.pop("reason", None)
    store.update(incoming)
    _sync_ai_worker_keys(store, incoming)
    _apply_tree_state(store, incoming)
    _apply_audio_reset(store, incoming)


__all__ = [
    "HealthCardSpec",
    "HEALTH_CARD_SPECS",
    "ai_pill_color",
    "format_cpu_card",
    "format_net_card",
    "format_ai_card",
    "format_audio_card",
    "format_process_tree_card",
    "format_inactivity_card",
    "format_health_tooltip",
    "merge_health_telemetry",
]
