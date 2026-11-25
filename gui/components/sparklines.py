# -*- coding: utf-8 -*-
"""
gui.components.sparklines: Real-time waveform canvas sparkline renderer.
Buffers rolling telemetry points and renders anti-aliased waveform line graphs with soft area fill.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 200 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from collections import deque
import tkinter as tk
from typing import Optional, List

from gui.theme import BG_SUBSURFACE, STATUS_EMERALD, ACCENT_CYAN


class CanvasSparkline(tk.Canvas):
    """
    Waveform canvas sparkline component.
    Maintains circular buffers (default 30 points) and renders smooth
    anti-aliased lines and translucent area fills. Supports single & dual trace.
    """

    def __init__(
        self,
        parent: tk.Widget,
        width: int = 180,
        height: int = 36,
        bg: str = BG_SUBSURFACE,
        line_color: str = STATUS_EMERALD,
        fill_color: Optional[str] = None,
        line_color2: str = "#6366F1",
        fill_color2: Optional[str] = None,
        maxlen: int = 30,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.canvas_width = width
        self.canvas_height = height
        self.line_color = line_color
        self.fill_color = fill_color
        self.line_color2 = line_color2
        self.fill_color2 = fill_color2
        self.maxlen = maxlen
        self.is_dual = False
        self.last_max_val = 100.0

        self.buffer: deque = deque([0.0] * maxlen, maxlen=maxlen)
        self.buffer2: deque = deque([0.0] * maxlen, maxlen=maxlen)

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event=None) -> None:
        """Handle canvas resize to redraw sparklines dynamically."""
        if event and event.width > 10 and event.height > 10:
            self.canvas_width = event.width
            self.canvas_height = event.height
            self._redraw()

    def push_value(self, val: float, max_val: float = 100.0) -> None:
        """Push a single metric value, update buffer, and render curve."""
        self.is_dual = False
        self.last_max_val = max(1.0, float(max_val))
        self.buffer.append(max(0.0, float(val)))
        self._redraw()

    def push_dual_values(self, val1: float, val2: float, max_val: float = 100.0) -> None:
        """Push dual values (e.g. download and upload) for dual-trace rendering."""
        self.is_dual = True
        self.last_max_val = max(1.0, float(max_val))
        self.buffer.append(max(0.0, float(val1)))
        self.buffer2.append(max(0.0, float(val2)))
        self._redraw()

    def clear(self) -> None:
        """Reset buffers and clear canvas."""
        self.buffer = deque([0.0] * self.maxlen, maxlen=self.maxlen)
        self.buffer2 = deque([0.0] * self.maxlen, maxlen=self.maxlen)
        self.delete("all")

    def _calculate_points(self, buf: deque, max_val: float) -> List[float]:
        """Normalize buffer values and compute canvas coordinate points."""
        w = max(self.canvas_width, self.winfo_width())
        h = max(self.canvas_height, self.winfo_height())
        pad_x, pad_y = 2, 3
        usable_w = max(10, w - 2 * pad_x)
        usable_h = max(10, h - 2 * pad_y)

        n = len(buf)
        if n < 2:
            return []

        points = []
        for i, v in enumerate(buf):
            norm = min(1.0, max(0.0, float(v) / max_val))
            x = pad_x + (i / (n - 1)) * usable_w
            y = (h - pad_y) - norm * usable_h
            points.extend([x, y])
        return points

    def _redraw(self) -> None:
        """Redraw sparkline traces and polygon area fills."""
        self.delete("all")
        h = max(self.canvas_height, self.winfo_height())

        # Render dual trace if active
        if self.is_dual:
            pts2 = self._calculate_points(self.buffer2, self.last_max_val)
            if len(pts2) >= 4:
                if self.fill_color2:
                    poly2 = [pts2[0], h, *pts2, pts2[-2], h]
                    self.create_polygon(poly2, fill=self.fill_color2, outline="", smooth=True)
                self.create_line(pts2, fill=self.line_color2, width=2, smooth=True)

        # Render primary trace
        pts = self._calculate_points(self.buffer, self.last_max_val)
        if len(pts) >= 4:
            if self.fill_color:
                poly = [pts[0], h, *pts, pts[-2], h]
                self.create_polygon(poly, fill=self.fill_color, outline="", smooth=True)
            self.create_line(pts, fill=self.line_color, width=2, smooth=True)
