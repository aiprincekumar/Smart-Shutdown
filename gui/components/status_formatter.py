# -*- coding: utf-8 -*-
"""
gui.components.status_formatter: Single-row dynamic status banner resolver,
mini progress indicators, and telemetry tooltip bindings for DashboardView.
Dept 05 Frontend & Desktop Engineering Compliant (Rule 28 < 250 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Dict, Any, Tuple, Optional, Callable

from gui.theme import (
    BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE, BG_BANNER_INHIBITED,
    STATUS_EMERALD, STATUS_AMBER, STATUS_CRIMSON, STATUS_ORANGE, STATUS_SLATE,
    ACCENT_CYAN, ACCENT_PURPLE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_BODY, FONT_BODY_BOLD,
)


def _format_empty_telemetry(bypass_active: bool) -> Tuple[str, str, str, str]:
    """Return default eligibility banner styling when telemetry is empty."""
    if bypass_active:
        return ("🛡 Inhibitors Bypassed — System Eligible for Shutdown", BORDER_BANNER_ELIGIBLE, BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE)
    return ("✔ System Eligible for Shutdown — No Inhibitors", BORDER_BANNER_ELIGIBLE, BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE)


def _resolve_active_countdown_banner(
    telemetry_data: Dict[str, Any],
    state: str,
    is_demo: bool,
    rem: int,
) -> Tuple[str, str, str, str]:
    """Resolve banner during active countdown or pre-shutdown grace window."""
    if is_demo:
        if "remaining" in telemetry_data and rem > 0:
            return (f"✔ Demo Mode — Simulated Countdown ({rem}s left)", "#34D399", "#152620", "#10B981")
        return ("✔ Demo Mode — Simulated Eligible for Shutdown", "#34D399", "#152620", "#10B981")
    grace_win = int(telemetry_data.get("grace_window", telemetry_data.get("pre_shutdown_close_window_sec", 30)))
    if state == "PRE_SHUTDOWN_GRACE" or rem <= grace_win:
        return (f"⏳ Countdown Running ({rem}s) — Grace period active", STATUS_ORANGE, "#2E1C12", STATUS_ORANGE)
    grace_in = max(0, rem - grace_win)
    return (f"⏳ Countdown Running ({rem}s) — Grace period in {grace_in}s", ACCENT_CYAN, "#0D222E", ACCENT_CYAN)


def _resolve_inhibited_banner(
    telemetry_data: Dict[str, Any],
    state: str,
    ai_st: str,
    cpu_safe: bool,
    net_idle: bool,
) -> Optional[Tuple[str, str, str, str]]:
    """Resolve inhibitor state based on AI, process, hardware, or user activity."""
    if "WAITING" in ai_st or "INPUT" in ai_st or "WAITING_USER" in state or bool(telemetry_data.get("gate_blocked", False)):
        return ("🛑 Shutdown Inhibited — Awaiting User Input", ACCENT_PURPLE, "#231B2E", ACCENT_PURPLE)

    workers = int(telemetry_data.get("subagent_count", telemetry_data.get("workers", telemetry_data.get("active_count", 0))))
    if workers > 0:
        return (f"🛑 Shutdown Inhibited — Active AI Work ({workers} subagent(s))", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)
    if "WORK" in ai_st or "BUSY" in ai_st:
        return ("🛑 Shutdown Inhibited — Active AI Work", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    if bool(telemetry_data.get("is_tree_busy", False)) or telemetry_data.get("reason") == "process_tree_busy":
        return ("🛑 Shutdown Inhibited — Descendant Processes Busy", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    audio_enabled = bool(telemetry_data.get("audio_inhibit_enabled", True))
    if audio_enabled and (bool(telemetry_data.get("audio_active", False)) or telemetry_data.get("reason") == "audio_active"):
        return ("🛑 Shutdown Inhibited — Audio Stream Active", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    if not cpu_safe or not net_idle or telemetry_data.get("reason") in ("hardware_busy", "cpu_busy", "network_busy"):
        cpu = telemetry_data.get("cpu_percent", telemetry_data.get("cpu_pct", 0.0))
        net = telemetry_data.get("net_total_kb", telemetry_data.get("net_kb_s", 0.0))
        return (f"🛑 Shutdown Inhibited — Hardware Busy (CPU: {cpu:.1f}% / Net: {net:.1f} KB/s)", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    idle = int(telemetry_data.get("idle_sec", telemetry_data.get("user_inactivity_sec", 0)))
    thresh = int(telemetry_data.get("inactivity_threshold_sec", telemetry_data.get("idle_threshold", 60)))
    if state in ("IDLE_MONITORING", "ABORTED_RESET") and idle < thresh and thresh > 0:
        return (f"🛑 Shutdown Inhibited — User Active ({idle}s < {thresh}s)", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    if (
        state == "BLOCKED"
        or bool(telemetry_data.get("is_blocked", False))
        or telemetry_data.get("eligible") is False
        or telemetry_data.get("is_eligible") is False
    ):
        return ("🛑 Shutdown Inhibited — Active Tasks Running", STATUS_AMBER, BG_BANNER_INHIBITED, STATUS_AMBER)

    return None


def resolve_eligibility_banner(
    telemetry_data: Dict[str, Any],
    bypass_active: bool,
    cpu_safe: bool,
    net_idle: bool,
    ai_st: str,
) -> Tuple[str, str, str, str]:
    """
    Resolve single-row dynamic eligibility banner state and styling.
    Returns: (text, fg_color, bg_color, border_color)
    """
    if not telemetry_data:
        return _format_empty_telemetry(bypass_active)

    target_mode = str(telemetry_data.get("target_mode", "")).upper()
    is_demo = bool(telemetry_data.get("is_demo", False)) or ("DEMO" in target_mode)
    raw_state = telemetry_data.get("state")
    state = str(raw_state if raw_state is not None else ("COUNTDOWN_ACTIVE" if is_demo else "IDLE_MONITORING")).upper()
    is_paused = bool(telemetry_data.get("is_paused", False)) or (state == "PAUSED")
    rem = int(telemetry_data.get("remaining", 0))

    if "SHUTDOWN_EXECUTED" in state:
        if is_demo:
            return ("✔ Demo Shutdown Complete — Simulation Dispatched", "#34D399", "#152620", "#10B981")
        return ("⚡ Shutdown Executed — System Halting", STATUS_CRIMSON, "#2D1518", STATUS_CRIMSON)

    if is_paused:
        return (f"⏸ Countdown Paused — {rem}s remaining", STATUS_AMBER, "#292015", STATUS_AMBER)

    if state in ("COUNTDOWN_ACTIVE", "PRE_SHUTDOWN_GRACE"):
        return _resolve_active_countdown_banner(telemetry_data, state, is_demo, rem)

    if bypass_active or bool(telemetry_data.get("bypass_inhibitors", False)):
        return ("🛡 Inhibitors Bypassed — System Eligible for Shutdown", BORDER_BANNER_ELIGIBLE, BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE)

    inhibited = _resolve_inhibited_banner(telemetry_data, state, ai_st, cpu_safe, net_idle)
    if inhibited is not None:
        return inhibited

    return ("✔ System Eligible for Shutdown — No Inhibitors", BORDER_BANNER_ELIGIBLE, BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE)


def render_mini_progress(canvas: tk.Canvas, pct: float, color: str) -> None:
    """Render a sleek horizontal mini progress pill with rounded caps on Canvas."""
    canvas.delete("all")
    canvas.create_line(4, 5, 40, 5, width=6, fill="#1E2738", capstyle="round")
    clamped = max(0.06, min(1.0, float(pct)))
    canvas.create_line(4, 5, 4 + int(36 * clamped), 5, width=6, fill=color, capstyle="round")


def render_status_pill(canvas: tk.Canvas, active: bool, color: str) -> None:
    """Render a sleek mini switch/status pill indicator dot on Canvas."""
    canvas.delete("all")
    canvas.create_line(6, 5, 38, 5, width=8, fill="#1E2738", capstyle="round")
    dot_x = 34 if active else 10
    canvas.create_oval(dot_x - 3, 2, dot_x + 3, 8, fill=color, outline="")


class TelemetryTooltip:
    """
    Lightweight, memory-leak-free hover tooltip displaying full telemetry metrics.
    Disappears immediately on mouse leave or button press with zero timer delays.
    """

    def __init__(self, widget: tk.Widget, get_text: Callable[[], str]):
        self.widget = widget
        self.get_text = get_text
        self.tip_window: Optional[tk.Toplevel] = None
        self.widget.bind("<Enter>", self.show_tip, add="+")
        self.widget.bind("<Leave>", self.hide_tip, add="+")
        self.widget.bind("<ButtonPress>", self.hide_tip, add="+")
        self.widget.bind("<Destroy>", self.hide_tip, add="+")

    def show_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window or not self.widget.winfo_exists():
            return
        text = self.get_text()
        if not text:
            return

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() - 32

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        frame = tk.Frame(tw, bg="#181B22", highlightbackground="#2E3444", highlightthickness=1, padx=8, pady=4)
        frame.pack()
        lbl = tk.Label(frame, text=text, font=FONT_BODY, fg=TEXT_PRIMARY, bg="#181B22")
        lbl.pack()

    def hide_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None


__all__ = [
    "resolve_eligibility_banner",
    "render_mini_progress",
    "render_status_pill",
    "TelemetryTooltip",
]
