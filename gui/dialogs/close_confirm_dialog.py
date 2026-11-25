# -*- coding: utf-8 -*-
"""
gui.dialogs.close_confirm_dialog: Fluent Dark exit confirmation modal dialog.
Decoupled from legacy gui.settings_window and styled via gui.theme tokens.
Department 05 Frontend & Desktop Engineering / Dept 04 UI/UX Design Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Callable, Optional

from gui.theme import (
    BG_BASE,
    BG_SURFACE,
    BG_HOVER,
    BORDER_MUTED,
    STATUS_CRIMSON,
    TEXT_PRIMARY,
    FONT_HEADER,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class CloseConfirmDialog(tk.Toplevel):
    """Dual-choice modal dialog when closing the Smart Shutdown window."""

    def __init__(
        self,
        parent: tk.Tk,
        on_minimize: Callable[[], None],
        on_exit: Callable[[], None],
    ):
        super().__init__(parent)
        self.parent = parent
        self.on_minimize = on_minimize
        self.on_exit = on_exit
        self.result: Optional[str] = None

        self.title("Smart Shutdown Exit")
        self.configure(bg=BG_BASE, highlightbackground=BORDER_MUTED, highlightthickness=1)
        self.geometry("340x170")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._center_dialog(parent)
        self._build_ui()

    def _center_dialog(self, parent: tk.Tk) -> None:
        """Center dialog relative to parent window."""
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + max(0, (parent.winfo_width() - 340) // 2)
            y = parent.winfo_rooty() + max(0, (parent.winfo_height() - 170) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        """Construct the prompt message and dual action buttons."""
        msg_frame = tk.Frame(self, bg=BG_BASE, padx=16, pady=16)
        msg_frame.pack(fill="both", expand=True)

        tk.Label(
            msg_frame,
            text="Close Smart Shutdown?\nChoose your preferred action:",
            font=FONT_HEADER,
            fg=TEXT_PRIMARY,
            bg=BG_BASE,
            justify="center",
        ).pack(pady=(0, 14))

        btn_box = tk.Frame(msg_frame, bg=BG_BASE)
        btn_box.pack(fill="x")
        self._build_action_buttons(btn_box)

    def _build_action_buttons(self, btn_box: tk.Frame) -> None:
        """Create Minimize to Tray and Exit Completely buttons."""
        tk.Button(
            btn_box, text="🗕 Minimize to Tray", font=FONT_BODY,
            bg=BG_SURFACE, fg=TEXT_PRIMARY, activebackground=BG_HOVER,
            activeforeground=TEXT_PRIMARY, highlightbackground=BORDER_MUTED,
            highlightthickness=1, relief="flat", padx=10, pady=5,
            cursor="hand2", command=self._handle_minimize,
        ).pack(side="left", expand=True, padx=4)

        tk.Button(
            btn_box, text="❌ Exit Completely", font=FONT_BODY_BOLD,
            bg=STATUS_CRIMSON, fg=TEXT_PRIMARY, activebackground="#DC2626",
            activeforeground=TEXT_PRIMARY, relief="flat", padx=10, pady=5,
            cursor="hand2", command=self._handle_exit,
        ).pack(side="right", expand=True, padx=4)

    def _handle_minimize(self) -> None:
        """User chose to minimize to background."""
        self.result = "minimize"
        self.destroy()
        if self.on_minimize:
            self.on_minimize()

    def _handle_exit(self) -> None:
        """User chose to exit completely."""
        self.result = "exit"
        self.destroy()
        if self.on_exit:
            self.on_exit()
