# -*- coding: utf-8 -*-
"""
gui.components.dashboard_view: Tab 1 Master Dashboard Cockpit View Component.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 350 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Optional, Callable, Dict, Any, Tuple

from gui.theme import (
    BG_BASE, BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED,
    BORDER_CARD, BORDER_CARD_HOVER, TRACK_RING,
    BG_BUTTON_SLATE, BORDER_BUTTON_SLATE,
    BG_BUTTON_ABORT, BORDER_BUTTON_ABORT, TEXT_BUTTON_ABORT,
    BG_BUTTON_BYPASS, BORDER_BUTTON_BYPASS, TEXT_BUTTON_BYPASS,
    BG_BUTTON_SHUTDOWN, BORDER_BUTTON_SHUTDOWN, TEXT_BUTTON_SHUTDOWN,
    BG_BANNER_ELIGIBLE, BORDER_BANNER_ELIGIBLE, BG_BANNER_INHIBITED,
    ACCENT_CYAN, ACCENT_PURPLE, STATUS_EMERALD, STATUS_AMBER,
    STATUS_CRIMSON, STATUS_SLATE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_CLOCK, FONT_BADGE, FONT_BODY, FONT_BODY_BOLD, FONT_HEALTH_HEADER,
)
from core.monitor_power import toggle_monitor_power_off
from gui.components.pill_button import PillButton
from gui.components.circular_gauge import CircularCountdownGauge
from gui.components.status_formatter import (
    resolve_eligibility_banner,
    render_mini_progress,
    render_status_pill,
    TelemetryTooltip,
)


class DashboardView(tk.Frame):
    """Tab 1 Dashboard: Advanced Luminous Windows 11 Fluent Dark monitoring cockpit."""

    def __init__(
        self, parent: tk.Widget,
        on_pause: Optional[Callable[[], None]] = None,
        on_snooze: Optional[Callable[[], None]] = None,
        on_toggle_monitor: Optional[Callable[[], None]] = None,
        on_abort: Optional[Callable[[], None]] = None,
        on_bypass_toggle: Optional[Callable[[], None]] = None,
        on_shutdown_now: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.on_pause = on_pause
        self.on_snooze = on_snooze
        self.on_toggle_monitor = on_toggle_monitor
        self.on_abort = on_abort
        self.on_bypass_toggle = on_bypass_toggle
        self.on_shutdown_now = on_shutdown_now
        self.is_paused = False
        self.bypass_active = False
        self.is_studio_view = True
        self._last_telemetry: Dict[str, Any] = {}
        self._build_components()
        self.set_studio_view(True)

    def _build_components(self) -> None:
        """Instantiate layout columns, circular gauge, health cards, eligibility banner, and 2x3 pill grid."""
        self.left_col = tk.Frame(self, bg=BG_BASE)
        self.right_col = tk.Frame(self, bg=BG_BASE)
        self._build_gauge_card()
        self._build_health_card()
        self._build_eligibility_card()
        self._build_action_grid()
        self.update_countdown(900, 900, False)

    def _build_gauge_card(self) -> None:
        """Instantiate modular 240x240 CircularCountdownGauge and link backward compatibility aliases."""
        self.gauge_card = CircularCountdownGauge(self.left_col)
        self.canvas_gauge = self.gauge_card.canvas
        self.lbl_clock = self.gauge_card.lbl_clock
        self.lbl_subtitle = self.gauge_card.lbl_subtitle
        self.canvas_prog = self.canvas_gauge
        self.lbl_timer = self.lbl_clock

    def _build_health_card(self) -> None:
        """Construct Informative Live Health Summary header and 4 independent floating cards."""
        self.health_card = tk.Frame(self.right_col, bg=BG_BASE, highlightthickness=0, padx=2, pady=2)
        tk.Label(self.health_card, text="Informative Live Health Summary", font=FONT_HEALTH_HEADER, fg=TEXT_PRIMARY, bg=BG_BASE).pack(anchor="w", pady=(0, 6))
        self.chip_cpu, self.bar_cpu = self._create_floating_card("CPU Activity", "0.0% [Safe]", STATUS_EMERALD)
        self.chip_net, self.bar_net = self._create_floating_card("Network Transfer", "0.0 KB/s [Idle]", STATUS_EMERALD)
        self.chip_ai, self.bar_ai = self._create_floating_card("Antigravity Task", "[ ✨ Ready ] All Done", STATUS_EMERALD, is_switch=True)
        self.chip_inactivity, self.bar_inactivity = self._create_floating_card("User Inactivity", "0s [Threshold: 60s]", STATUS_AMBER)

    def _create_floating_card(self, label_text: str, default_chip: str, chip_color: str, is_switch: bool = False) -> Tuple[tk.Label, tk.Canvas]:
        """Create an independent floating health card with green checkmark badge, metric label, and mini progress pill."""
        card_bg = "#141D2C"
        card = tk.Frame(self.health_card, bg=card_bg, highlightbackground=BORDER_CARD, highlightthickness=1, padx=12, pady=7)
        card.pack(fill="x", pady=3)
        left_box = tk.Frame(card, bg=card_bg)
        left_box.pack(side="left", anchor="w")
        tk.Label(left_box, text="✔ ", font=FONT_BODY_BOLD, fg=STATUS_EMERALD, bg=card_bg).pack(side="left")
        tk.Label(left_box, text=label_text, font=FONT_BODY, fg=TEXT_PRIMARY, bg=card_bg).pack(side="left")
        right_box = tk.Frame(card, bg=card_bg)
        right_box.pack(side="right", anchor="e")
        chip = tk.Label(right_box, text=default_chip, font=FONT_BODY_BOLD, fg=chip_color, bg=card_bg)
        chip.pack(side="left", padx=(0, 8))
        bar = tk.Canvas(right_box, width=44, height=10, bg=card_bg, highlightthickness=0, bd=0)
        bar.pack(side="left")
        if is_switch: self._update_status_pill(bar, False, STATUS_SLATE)
        else: self._update_mini_bar(bar, 0.0, chip_color)
        return chip, bar

    def _update_mini_bar(self, canvas: tk.Canvas, pct: float, color: str) -> None:
        """Render a sleek horizontal mini progress pill with rounded caps on Tkinter Canvas."""
        render_mini_progress(canvas, pct, color)

    def _update_status_pill(self, canvas: tk.Canvas, active: bool, color: str) -> None:
        """Render a sleek mini switch/status pill indicator."""
        render_status_pill(canvas, active, color)

    def _build_eligibility_card(self) -> None:
        """Construct dedicated status container and luminous dynamic single-row eligibility banner."""
        self.eligibility_card = tk.Frame(
            self.right_col, bg=BG_BANNER_ELIGIBLE, highlightbackground=BORDER_BANNER_ELIGIBLE, highlightthickness=1, padx=12, pady=9
        )
        self.lbl_eligibility = tk.Label(
            self.eligibility_card, text="✔  System Eligible for Shutdown — No Inhibitors",
            font=FONT_BODY_BOLD, fg=BORDER_BANNER_ELIGIBLE, bg=BG_BANNER_ELIGIBLE, padx=4, pady=2,
            wraplength=0,
        )
        self.lbl_eligibility.pack(fill="x", expand=True)

        # Attach telemetry hover tooltip for rich metrics inspection without popup delay
        self.tooltip = TelemetryTooltip(self.eligibility_card, self._format_tooltip_details)
        self.lbl_tooltip = TelemetryTooltip(self.lbl_eligibility, self._format_tooltip_details)

    def _format_tooltip_details(self) -> str:
        """Format a rich hover summary of system telemetry metrics."""
        if not self._last_telemetry:
            return ""
        cpu = self._last_telemetry.get("cpu_percent", self._last_telemetry.get("cpu_pct", 0.0))
        net = self._last_telemetry.get("net_total_kb", self._last_telemetry.get("net_kb_s", 0.0))
        idle = int(self._last_telemetry.get("idle_sec", 0))
        mode = self._last_telemetry.get("target_mode", "LIVE")
        state = self._last_telemetry.get("state", "IDLE_MONITORING")
        workers = self._last_telemetry.get("subagent_count", self._last_telemetry.get("workers", 0))
        return f"[{mode}] State: {state} | CPU: {cpu:.1f}% | Net: {net:.1f} KB/s | Idle: {idle}s | Workers: {workers}"

    def _build_action_grid(self) -> None:
        """Construct balanced 2x3 action grid holding exactly 6 ergonomic action pill buttons."""
        self.grid_frame = tk.Frame(self.left_col, bg=BG_BASE, highlightthickness=0, padx=4, pady=4)
        for c in range(3): self.grid_frame.grid_columnconfigure(c, weight=1, uniform="btn_col")
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)

        btn_specs = [
            ("btn_pause", "|| Pause", self._handle_pause, BG_BUTTON_SLATE, "#26344B", "#151E2B", BORDER_BUTTON_SLATE, "#3E5272", "#3E5272", "#FFFFFF", 0, 0),
            ("btn_snooze", "zᶻ +15m Snooze", self._handle_snooze, BG_BUTTON_SLATE, "#26344B", "#151E2B", BORDER_BUTTON_SLATE, "#3E5272", "#3E5272", "#FFFFFF", 0, 1),
            ("btn_monitor", "🖥 Toggle Monitor", self._handle_toggle_monitor, BG_BUTTON_SLATE, "#26344B", "#151E2B", BORDER_BUTTON_SLATE, "#3E5272", "#3E5272", "#FFFFFF", 0, 2),
            ("btn_abort", "✕ Abort", self._handle_abort, BG_BUTTON_ABORT, "#352920", "#181310", BORDER_BUTTON_ABORT, "#F59E0B", "#D97706", TEXT_BUTTON_ABORT, 1, 0),
            ("btn_bypass", "🛡 Bypass Blocks", self._handle_bypass_toggle, BG_BUTTON_BYPASS, "#1A3542", "#0D1C22", BORDER_BUTTON_BYPASS, "#22D3EE", "#0891B2", TEXT_BUTTON_BYPASS, 1, 1),
            ("btn_shutdown", "⚡ Shutdown Now", self._handle_shutdown_now, BG_BUTTON_SHUTDOWN, "#451A20", "#200D10", BORDER_BUTTON_SHUTDOWN, "#F87171", "#EF4444", TEXT_BUTTON_SHUTDOWN, 1, 2),
        ]
        for attr, txt, cmd, bg, hbg, pbg, bdr, hbdr, pbdr, fg, r, c in btn_specs:
            btn = PillButton(
                self.grid_frame, text=txt, command=cmd, normal_bg=bg, hover_bg=hbg, pressed_bg=pbg,
                border_color=bdr, hover_border=hbdr, pressed_border=pbdr, fg=fg, parent_bg=BG_BASE, corner_radius=12, height=42,
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            setattr(self, attr, btn)

        self.btn_cancel = self.btn_abort

    def _clear_layout_bindings(self) -> None:
        """Clear geometry managers for columns and child cards before layout switch."""
        for col in (self.left_col, self.right_col):
            col.pack_forget()
            col.grid_forget()
        for w in (self.gauge_card, self.grid_frame, self.health_card):
            w.pack_forget()
        if hasattr(self, "eligibility_card"):
            self.eligibility_card.pack_forget()

    def set_compact_view(self) -> None:
        """Switch to Compact single-column stacked layout."""
        self.is_studio_view = False
        self._clear_layout_bindings()
        self.grid_columnconfigure(0, weight=0, uniform="")
        self.grid_columnconfigure(1, weight=0, uniform="")
        self.grid_rowconfigure(0, weight=0)

        self.left_col.pack(side="top", fill="x", padx=4, pady=(2, 4))
        self.right_col.pack(side="top", fill="x", padx=4, pady=4)
        self.gauge_card.pack(fill="x", pady=(0, 4))
        self.grid_frame.pack(fill="x", pady=(4, 0))
        self.health_card.pack(fill="x", pady=(0, 4))
        if hasattr(self, "eligibility_card"):
            self.eligibility_card.pack(fill="x", pady=(4, 0))

    def set_studio_view(self, is_studio: bool = True) -> None:
        """Switch between Compact stacked layout and Studio dual-column layout."""
        if not is_studio:
            self.set_compact_view()
            return

        self.is_studio_view = True
        self._clear_layout_bindings()

        self.grid_columnconfigure(0, weight=1, uniform="studio_col")
        self.grid_columnconfigure(1, weight=1, uniform="studio_col")
        self.grid_rowconfigure(0, weight=1)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=4)
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=4)

        self.gauge_card.pack(fill="both", expand=True, pady=(0, 4))
        self.grid_frame.pack(fill="both", expand=True, pady=(4, 0))
        self.health_card.pack(fill="both", expand=True, pady=(0, 4))
        if hasattr(self, "eligibility_card"):
            self.eligibility_card.pack(fill="x", pady=(4, 0))

    def update_countdown(
        self,
        remaining_sec: int,
        total_sec: int,
        is_paused: bool = False,
        idle_sec: Optional[float] = None,
        idle_threshold: Optional[float] = None,
    ) -> None:
        """Update circular progress arcs, digital timer clock readout, and luminous glow transitions."""
        if idle_sec is None:
            idle_sec = self._last_telemetry.get("idle_sec", self._last_telemetry.get("user_inactivity_sec"))
        if idle_threshold is None:
            idle_threshold = self._last_telemetry.get("inactivity_threshold_sec", self._last_telemetry.get("idle_threshold"))
        self.gauge_card.update_countdown(
            remaining_sec, total_sec, is_paused,
            idle_sec=idle_sec, idle_threshold=idle_threshold,
            state_name=self._last_telemetry.get("state"),
            has_user_input=self._last_telemetry.get("has_user_input"),
        )
        self.set_pause_state(is_paused)

    def update_health(self, telemetry_data: Dict[str, Any]) -> None:
        """Update live telemetry chips, mini progress pills, and dynamic eligibility banner."""
        if not telemetry_data:
            return
        if "state" in telemetry_data and "reason" not in telemetry_data:
            self._last_telemetry.pop("reason", None)
        self._last_telemetry.update(telemetry_data)
        if "subagent_count" in telemetry_data and "workers" not in telemetry_data:
            self._last_telemetry["workers"] = telemetry_data["subagent_count"]
        elif "workers" in telemetry_data and "subagent_count" not in telemetry_data:
            self._last_telemetry["subagent_count"] = telemetry_data["workers"]
        cpu_safe, net_idle = self._update_hw_telemetry(self._last_telemetry)
        ai_st = self._update_ai_telemetry(self._last_telemetry)
        self._update_eligibility_banner(self._last_telemetry, cpu_safe, net_idle, ai_st)

    def _update_hw_telemetry(self, data: Dict[str, Any]) -> Tuple[bool, bool]:
        """Update CPU, Network, and User Inactivity telemetry indicators."""
        cpu = data.get("cpu_percent", data.get("cpu_pct", 0.0))
        cpu_safe = cpu < data.get("cpu_threshold", 15.0)
        cpu_color = STATUS_EMERALD if cpu_safe else STATUS_AMBER
        self.chip_cpu.config(text=f"{cpu:.1f}% [Safe]" if cpu_safe else f"{cpu:.1f}% [Spike]", fg=cpu_color)
        self._update_mini_bar(self.bar_cpu, cpu / 100.0, cpu_color)

        net = data.get("net_total_kb", data.get("net_kb_s", 0.0))
        net_thresh = data.get("net_threshold", 50.0)
        net_idle = (net < net_thresh) if net_thresh > 0.0 else (net <= 0.0)
        net_color = STATUS_EMERALD if net_idle else STATUS_AMBER
        self.chip_net.config(text=f"{net:.1f} KB/s [Idle]" if net_idle else f"{net:.1f} KB/s [Busy]", fg=net_color)
        self._update_mini_bar(self.bar_net, net / max(net_thresh * 2, 50.0), net_color)

        raw_idle = data.get("idle_sec") if data.get("idle_sec") is not None else data.get("user_inactivity_sec")
        raw_thresh = data.get("inactivity_threshold_sec") if data.get("inactivity_threshold_sec") is not None else data.get("idle_threshold")
        idle_s = int(0 if raw_idle is None else raw_idle)
        thresh_s = int(60 if raw_thresh is None else raw_thresh)
        inact_color = STATUS_EMERALD if idle_s >= thresh_s else STATUS_AMBER
        if thresh_s <= 60:
            txt = f"{idle_s}s [Threshold: {thresh_s}s]"
        elif thresh_s % 60 == 0 and idle_s % 60 == 0:
            txt = f"{idle_s // 60} mins [Threshold: {thresh_s // 60} mins]"
        else:
            txt = f"{idle_s // 60}m {idle_s % 60}s [Threshold: {thresh_s // 60}m]"
        self.chip_inactivity.config(text=txt, fg=inact_color)
        self._update_mini_bar(self.bar_inactivity, idle_s / max(thresh_s, 1), inact_color)
        return cpu_safe, net_idle

    def _update_ai_telemetry(self, data: Dict[str, Any]) -> str:
        """Update Antigravity AI Engine status chip and indicator pill."""
        ai_st = str(data.get("ai_state", self._last_telemetry.get("ai_state", "READY")) or "READY").upper()
        raw_workers = data.get("subagent_count", data.get("workers", self._last_telemetry.get("workers", 0)))
        try:
            workers = int(0 if raw_workers is None else raw_workers)
        except (TypeError, ValueError):
            workers = 0
        if "WAITING" in ai_st or "INPUT" in ai_st:
            self.chip_ai.config(text="[ 💬 Waiting ] Pending", fg=ACCENT_PURPLE)
            self._update_status_pill(self.bar_ai, False, ACCENT_PURPLE)
        elif workers > 0:
            self.chip_ai.config(text=f"Active AI Work ({workers} Active)", fg=ACCENT_CYAN)
            self._update_status_pill(self.bar_ai, True, STATUS_EMERALD)
        elif "WORK" in ai_st or "BUSY" in ai_st:
            self.chip_ai.config(text="[ ⚙️ Working ] Background Tasks", fg=STATUS_AMBER)
            self._update_status_pill(self.bar_ai, True, STATUS_AMBER)
        else:
            self.chip_ai.config(text="[ ✨ Ready ] All Done", fg=STATUS_EMERALD)
            self._update_status_pill(self.bar_ai, False, STATUS_SLATE)
        return ai_st

    def _update_eligibility_banner(self, telemetry_data: Dict[str, Any], cpu_safe: bool, net_idle: bool, ai_st: str) -> None:
        """Update eligibility banner text, icon, border glow, and container background via status_formatter."""
        if not hasattr(self, "lbl_eligibility"): return
        text, fg, bg, border = resolve_eligibility_banner(
            telemetry_data=telemetry_data,
            bypass_active=self.bypass_active,
            cpu_safe=cpu_safe,
            net_idle=net_idle,
            ai_st=ai_st,
        )
        self.eligibility_card.config(bg=bg, highlightbackground=border)
        self.lbl_eligibility.config(text=text, fg=fg, bg=bg)

    def _recalculate_eligibility(self) -> None:
        """Recalculate eligibility banner from last known telemetry state."""
        cpu = self._last_telemetry.get("cpu_percent", self._last_telemetry.get("cpu_pct", 0.0))
        net = self._last_telemetry.get("net_total_kb", self._last_telemetry.get("net_kb_s", 0.0))
        cpu_safe = cpu < self._last_telemetry.get("cpu_threshold", 15.0)
        net_thresh = self._last_telemetry.get("net_threshold", 50.0)
        net_idle = (net < net_thresh) if net_thresh > 0.0 else (net <= 0.0)
        ai_st = str(self._last_telemetry.get("ai_state", "READY")).upper()
        self._update_eligibility_banner(self._last_telemetry, cpu_safe, net_idle, ai_st)

    def set_pause_state(self, is_paused: bool, is_idle: bool = False) -> None:
        """Update pause button text, internal flag, and synced eligibility banner."""
        self.is_paused = is_paused
        if is_paused: self.btn_pause.config(text="▶ Resume")
        elif is_idle: self.btn_pause.config(text="|| Pause")
        else: self.btn_pause.config(text="|| Pause")
        if self._last_telemetry:
            self._last_telemetry["is_paused"] = is_paused
            self._recalculate_eligibility()

    def set_bypass_state(self, active: bool) -> None:
        """Update bypass button highlight, text state, and eligibility badge."""
        self.bypass_active = active
        bg_col = "#103540" if active else BG_BUTTON_BYPASS
        hov_col = "#184D5D" if active else "#1A3542"
        prs_col = "#0B252E" if active else "#0D1C22"
        self.btn_bypass.set_colors(
            normal_bg=bg_col, hover_bg=hov_col, pressed_bg=prs_col,
            border_color=BORDER_BUTTON_BYPASS, hover_border="#22D3EE", pressed_border="#0891B2",
            fg=TEXT_BUTTON_BYPASS,
        )
        self.btn_bypass.config(text="🛡 Bypass: ON" if active else "🛡 Bypass Blocks")
        self._recalculate_eligibility()

    def _handle_pause(self) -> None:
        if self.on_pause: self.on_pause()

    def _handle_snooze(self) -> None:
        if self.on_snooze: self.on_snooze()

    def _handle_toggle_monitor(self) -> None:
        if self.on_toggle_monitor: self.on_toggle_monitor()
        else: toggle_monitor_power_off()

    def _handle_abort(self) -> None:
        if self.on_abort: self.on_abort()

    def _handle_bypass_toggle(self) -> None:
        if self.on_bypass_toggle: self.on_bypass_toggle()
        else: self.set_bypass_state(not self.bypass_active)

    def _handle_shutdown_now(self) -> None:
        if self.on_shutdown_now: self.on_shutdown_now()
