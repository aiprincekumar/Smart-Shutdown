# -*- coding: utf-8 -*-
"""
gui.components.circular_gauge: Modular 240x240 Circular Countdown Gauge Component.
Features dual concentric rings: Master Shutdown Countdown (outer ring) and
Physical User Inactivity Timer (inner ring), with high-contrast digital readout.
Department 05 Frontend and Desktop Engineering Compliant (Rule 28 under 250 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import math
import tkinter as tk
from typing import Optional, Any, Tuple

from gui.components.status_resolver import resolve_input_activity_state
from gui.theme import (
    BG_BASE, TRACK_RING, HALO_CYAN, HALO_AMBER, HALO_CRIMSON,
    ACCENT_CYAN, STATUS_EMERALD, STATUS_AMBER, STATUS_CRIMSON,
    TEXT_PRIMARY, TEXT_MUTED, FONT_CLOCK, FONT_BADGE,
)


class CircularCountdownGauge(tk.Frame):
    """
    240x240 multi-layer concentric dual-ring countdown gauge.
    Outer Ring: Master Shutdown Countdown (10px stroke, 16px glowing halo).
    Inner Ring: Physical User Inactivity Timer (4px stroke, dynamic color).
    Center: High-contrast digital countdown clock, status subtitle, and inactivity readout.
    """

    _DYNAMIC_TAGS = (
        "halo", "halo_outer", "arc", "arc_outer",
        "cap", "cap_outer", "arc_inner", "cap_inner",
    )

    def __init__(self, parent: tk.Widget, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, highlightthickness=0, bd=0, **kwargs)
        self.canvas = tk.Canvas(
            self, width=240, height=240, bg=BG_BASE,
            highlightthickness=0, bd=0
        )
        self.canvas.pack(anchor="center", pady=(2, 4))
        self.canvas.create_oval(
            16, 16, 224, 224, outline=TRACK_RING, width=10, tags=("track", "track_outer")
        )
        self.canvas.create_oval(
            28, 28, 212, 212, outline="#181F2A", width=4, tags="track_inner"
        )
        self._build_center_labels()
        self.update_countdown(900, 900, False)

    def _build_center_labels(self) -> None:
        """Create centered digital clock, status subtitle, and inactivity readout."""
        self.center_frame = tk.Frame(self.canvas, bg=BG_BASE)
        self.lbl_clock = tk.Label(
            self.center_frame, text="15:00", font=FONT_CLOCK,
            fg=TEXT_PRIMARY, bg=BG_BASE
        )
        self.lbl_clock.pack(pady=(0, 1))
        self.lbl_subtitle = tk.Label(
            self.center_frame, text="MINUTES REMAINING", font=FONT_BADGE,
            fg=TEXT_MUTED, bg=BG_BASE
        )
        self.lbl_subtitle.pack(pady=(0, 1))
        self.lbl_inactivity = tk.Label(
            self.center_frame, text="USER IDLE", font=FONT_BADGE,
            fg="#94A3B8", bg=BG_BASE
        )
        self.lbl_inactivity.pack()
        self.center_win = self.canvas.create_window(
            120, 120, window=self.center_frame, tags="center_win"
        )

    def _update_center_labels(
        self,
        remaining_sec: int,
        is_paused: bool,
        idle_sec: Optional[float],
        idle_threshold: Optional[float],
        state_name: Optional[str] = None,
        has_user_input: Optional[bool] = None,
    ) -> None:
        """Update center clock text, pause subtitle, and unified presence/inactivity label."""
        m, s = remaining_sec // 60, remaining_sec % 60
        self.lbl_clock.config(text=f"{m:02d}:{s:02d}")
        self.lbl_subtitle.config(
            text="COUNTDOWN PAUSED" if is_paused else "MINUTES REMAINING",
            fg=STATUS_AMBER if is_paused else TEXT_MUTED,
        )
        phase = resolve_input_activity_state(
            state_name=state_name, idle_sec=idle_sec, idle_threshold=idle_threshold,
            has_user_input=has_user_input,
        )
        has_timer = idle_sec is not None and int(idle_sec) > 0 and idle_threshold and idle_threshold > 0
        if has_timer:
            im, isec = int(idle_sec) // 60, int(idle_sec) % 60
            tm, tsec = int(idle_threshold) // 60, int(idle_threshold) % 60
            txt = f"{phase}: {im:02d}:{isec:02d} / {tm:02d}:{tsec:02d}"
            fg = "#34D399" if phase in ("AWAY", "ACTIVE") else "#C084FC"
        else:
            txt = f"USER {phase}"
            fg = "#34D399" if phase in ("AWAY", "ACTIVE") else "#94A3B8"
        self.lbl_inactivity.config(text=txt, fg=fg)

    def _resolve_outer_colors(
        self, remaining_sec: int, pct: float, is_paused: bool
    ) -> Tuple[str, str]:
        """Resolve primary arc and outer glow halo colors from countdown state."""
        if remaining_sec <= 30:
            return STATUS_CRIMSON, HALO_CRIMSON
        if remaining_sec <= 60 or is_paused:
            return STATUS_AMBER, HALO_AMBER
        if pct < 0.4:
            return STATUS_EMERALD, "#083328"
        return ACCENT_CYAN, HALO_CYAN

    def _draw_outer_ring(
        self, remaining_sec: int, total_sec: int, is_paused: bool
    ) -> None:
        """Draw outer countdown halo, core arc, and rounded caps (clamped < 360)."""
        pct = max(0.0, min(1.0, remaining_sec / total_sec))
        extent = min(359.9, 360.0 * pct) if pct > 0 else 0.0
        if extent <= 0:
            return
        arc_color, halo_color = self._resolve_outer_colors(remaining_sec, pct, is_paused)
        self.canvas.create_arc(
            16, 16, 224, 224, start=90, extent=-extent,
            style="arc", width=16, outline=halo_color, tags=("halo", "halo_outer"),
        )
        self.canvas.create_arc(
            16, 16, 224, 224, start=90, extent=-extent,
            style="arc", width=10, outline=arc_color, tags=("arc", "arc_outer"),
        )
        self.canvas.create_oval(
            115, 11, 125, 21, fill=arc_color, outline="", tags=("cap", "cap_outer")
        )
        rad = math.radians(90 - extent)
        ex = 120 + 104 * math.cos(rad)
        ey = 120 - 104 * math.sin(rad)
        self.canvas.create_oval(
            ex - 5, ey - 5, ex + 5, ey + 5,
            fill=arc_color, outline="", tags=("cap", "cap_outer"),
        )

    def _draw_inner_ring(
        self, idle_sec: Optional[float], idle_threshold: Optional[float]
    ) -> None:
        """Draw inner physical user inactivity ring and rounded end caps."""
        if idle_sec is None or not idle_threshold or idle_threshold <= 0:
            return
        idle_ratio = max(0.0, min(1.0, float(idle_sec) / float(idle_threshold)))
        inner_extent = min(359.9, 360.0 * idle_ratio) if idle_ratio > 0 else 0.0
        if inner_extent <= 0:
            return
        if idle_ratio > 0.85:
            inner_color = "#F59E0B"
        elif idle_ratio >= 0.50:
            inner_color = "#8B5CF6"
        else:
            inner_color = "#10B981"
        self.canvas.create_arc(
            28, 28, 212, 212, start=90, extent=-inner_extent,
            style="arc", width=4, outline=inner_color, tags="arc_inner",
        )
        self.canvas.create_oval(
            118, 26, 122, 30, fill=inner_color, outline="", tags="cap_inner"
        )
        inner_rad = math.radians(90 - inner_extent)
        ix = 120 + 92 * math.cos(inner_rad)
        iy = 120 - 92 * math.sin(inner_rad)
        self.canvas.create_oval(
            ix - 2, iy - 2, ix + 2, iy + 2,
            fill=inner_color, outline="", tags="cap_inner",
        )

    def update_countdown(
        self,
        remaining_sec: int,
        total_sec: int,
        is_paused: bool = False,
        idle_sec: Optional[float] = None,
        idle_threshold: Optional[float] = None,
        state_name: Optional[str] = None,
        has_user_input: Optional[bool] = None,
    ) -> None:
        """Update outer and inner circular progress arcs, digital clock, and glow transitions."""
        remaining_sec = max(0, remaining_sec)
        total_sec = max(1, total_sec)
        self._update_center_labels(
            remaining_sec, is_paused, idle_sec, idle_threshold,
            state_name=state_name, has_user_input=has_user_input,
        )
        for tag in self._DYNAMIC_TAGS:
            self.canvas.delete(tag)
        self._draw_outer_ring(remaining_sec, total_sec, is_paused)
        self._draw_inner_ring(idle_sec, idle_threshold)
        self.canvas.tag_raise(self.center_win)
