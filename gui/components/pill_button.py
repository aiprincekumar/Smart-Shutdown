# -*- coding: utf-8 -*-
"""
gui.components.pill_button: Fluent Dark rounded pill button with Pillow anti-aliased rendering.
Subclasses tk.Button to preserve 100% backward compatibility and Tkinter button semantics.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 300 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Optional, Callable, Any
from PIL import Image, ImageDraw, ImageTk

from gui.theme import (
    BG_BASE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED,
    TEXT_PRIMARY, FONT_BODY_BOLD,
)


class PillButton(tk.Button):
    """
    Windows 11 Fluent Dark rounded pill button.
    Subclasses tk.Button directly so isinstance(btn, tk.Button) is True.
    Uses Pillow 3x supersampling with Lanczos downsampling to render smooth
    rounded pill backgrounds with seamless outside corners matching parent_bg.
    """

    def __init__(
        self, parent: tk.Widget, text: str = "", command: Optional[Callable[[], None]] = None,
        font: Any = FONT_BODY_BOLD, normal_bg: str = BG_SUBSURFACE, hover_bg: str = BG_HOVER,
        pressed_bg: str = "#1A1F29", border_color: str = BORDER_MUTED, hover_border: Optional[str] = None,
        pressed_border: Optional[str] = None, fg: str = TEXT_PRIMARY, parent_bg: str = BG_BASE,
        corner_radius: int = 10, width: int = 120, height: int = 42, **kwargs: Any,
    ):
        self._init_button_state(
            normal_bg, hover_bg, pressed_bg, border_color, hover_border,
            pressed_border, parent_bg, corner_radius, width, height
        )
        cursor = kwargs.pop("cursor", "hand2")
        for k in ("highlightthickness", "relief", "bd", "compound", "padx", "pady"):
            kwargs.pop(k, None)

        super().__init__(
            parent, text=text, command=command, font=font, fg=fg, bg=parent_bg,
            activebackground=parent_bg, activeforeground=fg, relief="flat", bd=0,
            highlightthickness=0, compound="center", cursor=cursor, **kwargs
        )
        self._render_pills(self._curr_w, self._curr_h)
        self._apply_photo(self._normal_photo)
        self._bind_pill_events()

    def _init_button_state(
        self, normal_bg: str, hover_bg: str, pressed_bg: str, border_color: str,
        hover_border: Optional[str], pressed_border: Optional[str], parent_bg: str,
        corner_radius: int, width: int, height: int
    ) -> None:
        """Initialize color properties and dimensions."""
        self.normal_bg = normal_bg
        self._hover_bg = hover_bg
        self.pressed_bg = pressed_bg
        self.border_color = border_color
        self.hover_border = hover_border or border_color
        self.pressed_border = pressed_border or border_color
        self.parent_bg = parent_bg
        self.corner_radius = corner_radius
        self._curr_w, self._curr_h = max(20, width), max(20, height)
        self._is_pressed, self._is_hovered = False, False
        self._normal_photo: Optional[ImageTk.PhotoImage] = None
        self._hover_photo: Optional[ImageTk.PhotoImage] = None
        self._pressed_photo: Optional[ImageTk.PhotoImage] = None
        self._current_photo: Optional[ImageTk.PhotoImage] = None

    def _bind_pill_events(self) -> None:
        """Bind interactive mouse, resize, and destroy event listeners."""
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.bind("<Button-1>", self._on_press, add="+")
        self.bind("<ButtonRelease-1>", self._on_release, add="+")
        self.bind("<Configure>", self._on_configure, add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _on_destroy(self, event: Optional[tk.Event] = None) -> None:
        """Release PhotoImage references cleanly on widget destruction."""
        if event is not None and event.widget is not self:
            return
        try:
            self._normal_photo = None
            self._hover_photo = None
            self._pressed_photo = None
            self._current_photo = None
        except Exception:
            pass

    @property
    def default_bg(self) -> str:
        """Alias for normal background color."""
        return self.normal_bg

    @default_bg.setter
    def default_bg(self, val: str) -> None:
        self.normal_bg = val

    @property
    def hover_bg(self) -> str:
        """Alias for hover background color."""
        return self._hover_bg

    @hover_bg.setter
    def hover_bg(self, val: str) -> None:
        self._hover_bg = val

    def set_colors(
        self,
        normal_bg: Optional[str] = None,
        hover_bg: Optional[str] = None,
        pressed_bg: Optional[str] = None,
        border_color: Optional[str] = None,
        hover_border: Optional[str] = None,
        pressed_border: Optional[str] = None,
        fg: Optional[str] = None,
    ) -> None:
        """Dynamically update pill color profiles with live re-rendering."""
        if normal_bg is not None:
            self.normal_bg = normal_bg
        if hover_bg is not None:
            self._hover_bg = hover_bg
        if pressed_bg is not None:
            self.pressed_bg = pressed_bg
        if border_color is not None:
            self.border_color = border_color
            if hover_border is None:
                self.hover_border = border_color
            if pressed_border is None:
                self.pressed_border = border_color
        if hover_border is not None:
            self.hover_border = hover_border
        if pressed_border is not None:
            self.pressed_border = pressed_border
        if fg is not None:
            super().configure(fg=fg, activeforeground=fg)

        if self._curr_w > 10 and self._curr_h > 10:
            self._render_pills(self._curr_w, self._curr_h)
            target = self._hover_photo if self._is_hovered else self._normal_photo
            self._apply_photo(target)

    def configure(self, cnf=None, **kwargs: Any) -> Any:
        """Intercept configure/config calls to preserve pill styling."""
        re_render = False
        if "normal_bg" in kwargs:
            self.normal_bg = kwargs.pop("normal_bg")
            re_render = True
        if "border_color" in kwargs:
            self.border_color = kwargs.pop("border_color")
            re_render = True
        if "hover_bg" in kwargs:
            self._hover_bg = kwargs.pop("hover_bg")
            re_render = True
        if "bg" in kwargs:
            new_bg = kwargs["bg"]
            if new_bg != self.parent_bg:
                self.normal_bg = new_bg
                re_render = True
                kwargs["bg"] = self.parent_bg
        if "highlightbackground" in kwargs:
            self.border_color = kwargs.pop("highlightbackground")
            re_render = True

        res = super().configure(cnf, **kwargs)
        if re_render and self._curr_w > 10 and self._curr_h > 10:
            self._render_pills(self._curr_w, self._curr_h)
            target = self._hover_photo if self._is_hovered else self._normal_photo
            self._apply_photo(target)
        return res

    config = configure

    def _create_pill_image(self, w: int, h: int, bg_color: str, border_col: str) -> Optional[ImageTk.PhotoImage]:
        """Generate anti-aliased rounded rectangle pill image using 3x supersampling."""
        try:
            scale = 3
            sw, sh = w * scale, h * scale
            img = Image.new("RGB", (sw, sh), self.parent_bg)
            draw = ImageDraw.Draw(img)
            r = min(self.corner_radius, max(2, (h - 2) // 2)) * scale
            pad = scale // 2
            draw.rounded_rectangle(
                [pad, pad, sw - 1 - pad, sh - 1 - pad],
                radius=r,
                fill=bg_color,
                outline=border_col,
                width=max(1, scale),
            )
            resized = img.resize((w, h), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized, master=self)
        except Exception:
            return None

    def _render_pills(self, w: int, h: int) -> None:
        """Re-render normal, hover, and pressed pill state images."""
        self._curr_w, self._curr_h = max(20, w), max(20, h)
        self._normal_photo = self._create_pill_image(self._curr_w, self._curr_h, self.normal_bg, self.border_color)
        self._hover_photo = self._create_pill_image(self._curr_w, self._curr_h, self._hover_bg, self.hover_border)
        self._pressed_photo = self._create_pill_image(self._curr_w, self._curr_h, self.pressed_bg, self.pressed_border)

    def _apply_photo(self, photo: Optional[ImageTk.PhotoImage]) -> None:
        """Apply PhotoImage to button and retain python reference to prevent GC."""
        if photo is not None and self.winfo_exists():
            self._current_photo = photo
            try:
                super().configure(image=photo)
            except tk.TclError:
                pass

    def _on_enter(self, event: Optional[tk.Event] = None) -> None:
        self._is_hovered = True
        if not self._is_pressed and self._hover_photo:
            self._apply_photo(self._hover_photo)

    def _on_leave(self, event: Optional[tk.Event] = None) -> None:
        self._is_hovered = False
        self._is_pressed = False
        if self._normal_photo:
            self._apply_photo(self._normal_photo)

    def _on_press(self, event: Optional[tk.Event] = None) -> None:
        self._is_pressed = True
        if self._pressed_photo:
            self._apply_photo(self._pressed_photo)

    def _on_release(self, event: Optional[tk.Event] = None) -> None:
        self._is_pressed = False
        target = self._hover_photo if self._is_hovered else self._normal_photo
        if target:
            self._apply_photo(target)

    def _on_configure(self, event: tk.Event) -> None:
        """Handle resize reflow and regenerate anti-aliased pills if size changed."""
        if not self.winfo_exists():
            return
        w, h = event.width, event.height
        if w > 20 and h > 20 and (abs(w - self._curr_w) > 2 or abs(h - self._curr_h) > 2):
            self._render_pills(w, h)
            target = self._pressed_photo if self._is_pressed else (
                self._hover_photo if self._is_hovered else self._normal_photo
            )
            self._apply_photo(target)
