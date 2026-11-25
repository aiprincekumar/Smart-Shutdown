# -*- coding: utf-8 -*-
"""
gui.components.modern_checkbox: Modern Canvas-based Checkbox Widgets.
Implements ModernCheckbox (boolean) and TriStateCheckbox (indeterminate/partial)
with Fluent Dark styling, vector checkmarks, hover glow, and variable two-way sync.
Department 05 Frontend & Desktop Engineering Compliant (Universal Rule 28 < 200 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Optional, Callable, Any


class _BaseCanvasCheckbox(tk.Canvas):
    """Base canvas widget providing chamfered rounded box and vector drawing."""

    def __init__(self, parent: tk.Widget, size: int = 18, bg: Optional[str] = None, **kwargs: Any):
        self.size = size
        self._hovered = False
        super().__init__(
            parent, width=size, height=size, bg=bg or parent.cget("bg"),
            highlightthickness=0, bd=0, cursor="hand2", **kwargs
        )
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _: self._set_hover(True))
        self.bind("<Leave>", lambda _: self._set_hover(False))

    def _set_hover(self, hovered: bool) -> None:
        self._hovered = hovered
        self._draw()

    def _draw_box(self, fill: str, outline: str) -> None:
        x1, y1, x2, y2 = 1, 1, self.size - 2, self.size - 2
        r = min(2, (x2 - x1) // 3)
        pts = [x1 + r, y1, x2 - r, y1, x2, y1 + r, x2, y2 - r, x2 - r, y2, x1 + r, y2, x1, y2 - r, x1, y1 + r]
        self.create_polygon(pts, fill=fill, outline=outline, width=1)

    def _draw_checkmark(self) -> None:
        s = self.size
        self.create_line(
            s * 0.25, s * 0.50, s * 0.42, s * 0.70, s * 0.75, s * 0.28,
            fill="#FFFFFF", width=2, capstyle="round", joinstyle="round"
        )

    def _draw_dash(self) -> None:
        s = self.size
        self.create_line(s * 0.25, s * 0.50, s * 0.75, s * 0.50, fill="#06B6D4", width=2, capstyle="round")

    def _on_click(self, _event: tk.Event) -> None:
        raise NotImplementedError

    def _draw(self) -> None:
        raise NotImplementedError


class ModernCheckbox(_BaseCanvasCheckbox):
    """Modern Canvas-based Checkbox widget with two-way BooleanVar synchronization."""

    def __init__(
        self, parent: tk.Widget, variable: Optional[tk.BooleanVar] = None,
        command: Optional[Callable[[], None]] = None, size: int = 18, bg: Optional[str] = None, **kwargs: Any
    ):
        self.command = command
        self.variable = variable
        self._checked = bool(variable.get()) if variable is not None else False
        super().__init__(parent, size=size, bg=bg, **kwargs)
        if self.variable is not None:
            self.variable.trace_add("write", self._on_var_changed)
        self._draw()

    def get(self) -> bool:
        return self._checked

    def set(self, value: bool) -> None:
        self._checked = bool(value)
        if self.variable is not None and self.variable.get() != self._checked:
            self.variable.set(self._checked)
        self._draw()

    def toggle(self) -> None:
        self.set(not self._checked)

    def _on_click(self, _event: tk.Event) -> None:
        self.toggle()
        if self.command:
            self.command()

    def _on_var_changed(self, *_: Any) -> None:
        if self.variable is not None and self.variable.get() != self._checked:
            self._checked = bool(self.variable.get())
            self._draw()

    def _draw(self) -> None:
        self.delete("all")
        if self._checked:
            self._draw_box("#06B6D4", "#38BDF8" if self._hovered else "#0284C7")
            self._draw_checkmark()
        else:
            self._draw_box("#1E2430", "#3B4252" if self._hovered else "#2A303D")


class TriStateCheckbox(_BaseCanvasCheckbox):
    """Modern Canvas-based Tri-State Checkbox (0=Unchecked, 1=Partial, 2=Checked)."""

    STATE_UNCHECKED = 0
    STATE_PARTIAL = 1
    STATE_CHECKED = 2

    def __init__(
        self, parent: tk.Widget, command: Optional[Callable[..., None]] = None,
        size: int = 18, bg: Optional[str] = None, initial_state: int = STATE_UNCHECKED, **kwargs: Any
    ):
        self.command = command
        self._state = max(0, min(2, initial_state))
        super().__init__(parent, size=size, bg=bg, **kwargs)
        self._draw()

    def get_state(self) -> int:
        return self._state

    def set_state(self, state: int) -> None:
        self._state = max(0, min(2, int(state)))
        self._draw()

    def toggle(self) -> None:
        self._state = 0 if self._state == self.STATE_CHECKED else self.STATE_CHECKED
        self._draw()

    def _on_click(self, _event: tk.Event) -> None:
        self.toggle()
        if self.command:
            try:
                self.command(self._state)
            except TypeError:
                self.command()

    def _draw(self) -> None:
        self.delete("all")
        if self._state == self.STATE_CHECKED:
            self._draw_box("#06B6D4", "#38BDF8" if self._hovered else "#0284C7")
            self._draw_checkmark()
        elif self._state == self.STATE_PARTIAL:
            self._draw_box("#083344", "#22D3EE" if self._hovered else "#06B6D4")
            self._draw_dash()
        else:
            self._draw_box("#1E2430", "#3B4252" if self._hovered else "#2A303D")
