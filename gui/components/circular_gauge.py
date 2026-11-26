# -*- coding: utf-8 -*-
"""
gui.components.circular_gauge: Modular 268x268 Circular Countdown Gauge Component.
Features dual concentric rings: Master Shutdown Countdown (outer ring) and
Physical User Inactivity Timer (inner ring), with high-contrast digital readout.
Department 05 Frontend and Desktop Engineering Compliant (Rule 28 under 250 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from dataclasses import dataclass
import math
import tkinter as tk
from typing import Optional, Any, Tuple

from gui.components.status_resolver import resolve_input_activity_state
from gui.theme import (
    BG_BASE, TRACK_RING, HALO_CYAN, HALO_AMBER, HALO_CRIMSON,
    ACCENT_CYAN, STATUS_EMERALD, STATUS_AMBER, STATUS_CRIMSON,
    TEXT_PRIMARY, TEXT_MUTED, FONT_CLOCK, FONT_BADGE,
)


@dataclass(frozen=True)
class GaugeGeometry:
    """Scaled geometry and typography parameters for CircularCountdownGauge."""

    size: int
    center: float
    outer_bbox: Tuple[int, int, int, int]
    outer_radius: float
    outer_width: int
    outer_cap_r: float
    halo_width: int
    inner_bbox: Tuple[int, int, int, int]
    inner_radius: float
    inner_width: int
    inner_cap_r: float
    clock_font: Tuple[str, int, str]
    sub_font: Tuple[str, int, str]
    label_pady: int


def _build_gauge_geometry(size: int) -> GaugeGeometry:
    """Compute proportional gauge ring geometry and fonts from target canvas size."""
    canvas_size = max(120, int(size))
    scale = canvas_size / 240.0
    center = canvas_size / 2.0
    outer_pad = round(16 * scale)
    outer_width = max(2, round(10 * scale))
    halo_width = max(4, round(16 * scale))
    inner_pad = max(outer_pad + 12, round(28 * scale) + (1 if canvas_size > 240 else 0))
    inner_width = max(3, round(4.4 * scale))
    return GaugeGeometry(
        size=canvas_size,
        center=center,
        outer_bbox=(outer_pad, outer_pad, canvas_size - outer_pad, canvas_size - outer_pad),
        outer_radius=center - outer_pad,
        outer_width=outer_width,
        outer_cap_r=outer_width / 2.0,
        halo_width=halo_width,
        inner_bbox=(inner_pad, inner_pad, canvas_size - inner_pad, canvas_size - inner_pad),
        inner_radius=center - inner_pad,
        inner_width=inner_width,
        inner_cap_r=inner_width / 2.0,
        clock_font=(FONT_CLOCK[0], max(12, round(FONT_CLOCK[1] * scale)), FONT_CLOCK[2]),
        sub_font=(FONT_BADGE[0], max(8, round(FONT_BADGE[1] * scale)), FONT_BADGE[2]),
        label_pady=max(1, round(1.5 * scale)),
    )


def _compute_cap_ovals(
    center: float, radius: float, cap_r: float, extent: float
) -> Tuple[Tuple[float, float, float, float], Tuple[float, float, float, float]]:
    """Compute start (12 o'clock) and dynamic end cap oval bounding boxes."""
    start_box = (center - cap_r, center - radius - cap_r, center + cap_r, center - radius + cap_r)
    rad = math.radians(90 - extent)
    ex, ey = center + radius * math.cos(rad), center - radius * math.sin(rad)
    return start_box, (ex - cap_r, ey - cap_r, ex + cap_r, ey + cap_r)


class CircularCountdownGauge(tk.Frame):
    """
    268x268 multi-layer concentric dual-ring countdown gauge.
    Outer Ring: Master Shutdown Countdown (11px stroke, 18px glowing halo at 268px).
    Inner Ring: Physical User Inactivity Timer (5px stroke at 268px, dynamic color).
    Center: High-contrast digital countdown clock, status subtitle, and inactivity readout.
    """

    _DYNAMIC_TAGS = (
        "halo", "halo_outer", "arc", "arc_outer",
        "cap", "cap_outer", "arc_inner", "cap_inner",
    )

    def __init__(self, parent: tk.Widget, size: int = 268, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, highlightthickness=0, bd=0, **kwargs)
        self._geom = _build_gauge_geometry(size)
        g = self._geom
        self.canvas = tk.Canvas(
            self, width=g.size, height=g.size, bg=BG_BASE, highlightthickness=0, bd=0,
        )
        self.canvas.pack(anchor="center", expand=True, pady=(2, 4))
        self.canvas.create_oval(*g.outer_bbox, outline=TRACK_RING, width=g.outer_width, tags=("track", "track_outer"))
        self.canvas.create_oval(*g.inner_bbox, outline="#181F2A", width=g.inner_width, tags="track_inner")
        self._build_center_labels()
        self.update_countdown(900, 900, False)

    def _build_center_labels(self) -> None:
        """Create centered digital clock, status subtitle, and inactivity readout."""
        g = self._geom
        self.center_frame = tk.Frame(self.canvas, bg=BG_BASE)
        self.lbl_clock = tk.Label(self.center_frame, text="15:00", font=g.clock_font, fg=TEXT_PRIMARY, bg=BG_BASE)
        self.lbl_clock.pack(pady=(0, g.label_pady))
        self.lbl_subtitle = tk.Label(self.center_frame, text="MINUTES REMAINING", font=g.sub_font, fg=TEXT_MUTED, bg=BG_BASE)
        self.lbl_subtitle.pack(pady=(0, g.label_pady))
        self.lbl_inactivity = tk.Label(self.center_frame, text="USER IDLE", font=g.sub_font, fg="#94A3B8", bg=BG_BASE)
        self.lbl_inactivity.pack()
        self.center_win = self.canvas.create_window(g.center, g.center, window=self.center_frame, tags="center_win")

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
        g = self._geom
        arc_color, halo_color = self._resolve_outer_colors(remaining_sec, pct, is_paused)
        self.canvas.create_arc(
            *g.outer_bbox, start=90, extent=-extent,
            style="arc", width=g.halo_width, outline=halo_color, tags=("halo", "halo_outer"),
        )
        self.canvas.create_arc(
            *g.outer_bbox, start=90, extent=-extent,
            style="arc", width=g.outer_width, outline=arc_color, tags=("arc", "arc_outer"),
        )
        for bbox in _compute_cap_ovals(g.center, g.outer_radius, g.outer_cap_r, extent):
            self.canvas.create_oval(
                *bbox, fill=arc_color, outline="", tags=("cap", "cap_outer"),
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
        g = self._geom
        self.canvas.create_arc(
            *g.inner_bbox, start=90, extent=-inner_extent,
            style="arc", width=g.inner_width, outline=inner_color, tags="arc_inner",
        )
        for bbox in _compute_cap_ovals(g.center, g.inner_radius, g.inner_cap_r, inner_extent):
            self.canvas.create_oval(
                *bbox, fill=inner_color, outline="", tags="cap_inner",
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
