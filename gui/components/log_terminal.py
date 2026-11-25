# -*- coding: utf-8 -*-
"""
gui.components.log_terminal: Diagnostic Event Console.
Provides real-time scrollable logging with color-coded severity tags.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import time
import tkinter as tk
from tkinter import ttk

from gui.theme import (
    TERMINAL_BG,
    TERMINAL_TEXT,
    BG_SURFACE,
    BORDER_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_BLUE,
    STATUS_GREEN,
    STATUS_AMBER,
    STATUS_RED,
    FONT_SUBHEADER,
    FONT_BODY,
    FONT_TERMINAL,
)


class DiagnosticTerminal(tk.Frame):
    """Real-time scrollable diagnostic console with color tags."""

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=8, pady=6, **kwargs)
        self.auto_scroll = True
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct terminal header and scrolled text area."""
        # Header Row
        hdr = tk.Frame(self, bg=BG_SURFACE)
        hdr.pack(fill="x", pady=(0, 4))

        lbl = tk.Label(hdr, text="📋 Diagnostic Event Log", bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_SUBHEADER)
        lbl.pack(side="left")

        # Clear Button
        btn_clear = tk.Button(
            hdr, text="Clear", bg=TERMINAL_BG, fg=TEXT_SECONDARY,
            activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY, padx=6, pady=1, command=self.clear_logs
        )
        btn_clear.pack(side="right", padx=(4, 0))

        # Auto-scroll Toggle
        self.var_autoscroll = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(
            hdr, text="Auto-Scroll", variable=self.var_autoscroll,
            bg=BG_SURFACE, fg=TEXT_SECONDARY, selectcolor=TERMINAL_BG,
            activebackground=BG_SURFACE, activeforeground=TEXT_PRIMARY,
            font=FONT_BODY
        )
        chk.pack(side="right")

        # Scrolled Text Box
        box_frame = tk.Frame(self, bg=TERMINAL_BG)
        box_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            box_frame,
            bg=TERMINAL_BG,
            fg=TERMINAL_TEXT,
            font=FONT_TERMINAL,
            wrap="word",
            height=7,
            relief="flat",
            highlightthickness=0,
            padx=6,
            pady=4
        )
        self.scrollbar = tk.Scrollbar(box_frame, command=self.text_area.yview, bg=TERMINAL_BG)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)

        # Configure color tags
        self.text_area.tag_config("info", foreground="#80D8FF")
        self.text_area.tag_config("warn", foreground=STATUS_AMBER)
        self.text_area.tag_config("crit", foreground=STATUS_RED)
        self.text_area.tag_config("success", foreground="#69F0AE")
        self.text_area.tag_config("time", foreground="#707070")

    def append_log(self, message: str, level: str = "info") -> None:
        """Insert a timestamped log line with severity color tagging."""
        timestamp = time.strftime("[%H:%M:%S] ")
        tag = level.lower()
        if tag not in ("info", "warn", "crit", "success"):
            tag = "info"

        self.text_area.insert(tk.END, timestamp, "time")
        self.text_area.insert(tk.END, f"{message}\n", tag)

        if self.var_autoscroll.get():
            self.text_area.see(tk.END)

    def clear_logs(self) -> None:
        """Clear all entries from the terminal."""
        self.text_area.delete("1.0", tk.END)
