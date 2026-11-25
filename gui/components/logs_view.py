# -*- coding: utf-8 -*-
"""
gui.components.logs_view: Tab 3 Diagnostic Logs Terminal Component.
Houses single-row sub-tabs, search toolbar, syntax-highlighted terminal, and action bar.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 320 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import time
import tkinter as tk
from collections import deque
from typing import Optional, Deque, Dict, Any

from gui.theme import (
    BG_BASE, BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED,
    ACCENT_CYAN, STATUS_EMERALD, STATUS_AMBER, STATUS_CRIMSON, STATUS_SLATE,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_BADGE, FONT_BODY,
)


class LogsView(tk.Frame):
    """
    Tab 3 Logs View: Single-row sub-tabs ([Diagnostics] / [Errors]) + same-row search toolbar,
    color-tagged high-contrast terminal, and action bar (Copy All, Clear, Export).
    """

    MAX_ENTRIES = 2000
    _FILTER_LABELS = {
        "all": "All",
        "info": "Info",
        "health": "Health",
        "ai_gate": "AI Gate",
        "warn": "Warn",
        "crit": "Crit",
    }

    def __init__(self, parent: tk.Widget, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.active_subtab = "diagnostics"
        self.filter_level = "all"
        self.search_query = ""
        self.auto_scroll = True
        self._entries: Deque[Dict[str, str]] = deque(maxlen=self.MAX_ENTRIES)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct single-row toolbar, monospaced code terminal, and action bar."""
        self._build_toolbar()
        self._build_terminal_box()
        self._build_action_bar()
        self._update_subtab_styling()

    def _build_toolbar(self) -> None:
        """Construct single-row sub-navigation and search/filter controls."""
        self.toolbar = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.toolbar.pack(fill="x", padx=4, pady=(2, 4))

        left_subtabs = tk.Frame(self.toolbar, bg=BG_SURFACE)
        left_subtabs.pack(side="left")
        self.btn_subtab_diag = tk.Button(
            left_subtabs, text="📋 Diagnostics", font=FONT_BADGE, bg=BG_SUBSURFACE, fg=ACCENT_CYAN,
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2", command=lambda: self.set_subtab("diagnostics"),
        )
        self.btn_subtab_diag.pack(side="left", padx=(0, 2))
        self.btn_subtab_err = tk.Button(
            left_subtabs, text="⚠️ Errors", font=FONT_BADGE, bg=BG_SUBSURFACE, fg=TEXT_SECONDARY,
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2", command=lambda: self.set_subtab("errors"),
        )
        self.btn_subtab_err.pack(side="left", padx=2)

        right_controls = tk.Frame(self.toolbar, bg=BG_SURFACE)
        right_controls.pack(side="right")
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(
            right_controls, textvariable=self.search_var, bg=BG_SUBSURFACE, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, font=FONT_BODY, relief="flat", highlightthickness=1,
            highlightbackground=BORDER_MUTED, width=16,
        )
        self.entry_search.pack(side="left", padx=(0, 4))
        self.search_var.trace_add("write", lambda *_: self.filter_logs(self.search_var.get()))

        self.filter_var = tk.StringVar(value="All")
        self.opt_filter = tk.OptionMenu(
            right_controls, self.filter_var, "All", "Info", "Health", "AI Gate", "Warn", "Crit",
            command=self._on_filter_option_changed,
        )
        self.opt_filter.config(
            bg=BG_SUBSURFACE, fg=TEXT_SECONDARY, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
            font=FONT_BADGE, highlightthickness=1, highlightbackground=BORDER_MUTED, bd=0, relief="flat", cursor="hand2",
        )
        self.opt_filter["menu"].config(bg=BG_SURFACE, fg=TEXT_PRIMARY, activebackground=BG_HOVER, activeforeground=ACCENT_CYAN)
        self.opt_filter.pack(side="left")

    def _build_terminal_box(self) -> None:
        """Construct monospaced scrolling terminal text widget and tags."""
        self.box_frame = tk.Frame(self, bg="#0A0C10")
        self.box_frame.pack(fill="both", expand=True, padx=4, pady=2)
        self.text_area = tk.Text(
            self.box_frame, bg="#0A0C10", fg="#E0E0E0", font=("Consolas", 9), wrap="word",
            relief="flat", highlightthickness=0, padx=8, pady=6,
        )
        self.scrollbar = tk.Scrollbar(self.box_frame, command=self.text_area.yview, bg="#0A0C10")
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)
        self._configure_tags()

    def _build_action_bar(self) -> None:
        """Construct bottom action bar with Copy All, Clear Console, Export, and Auto-Scroll."""
        self.action_bar = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.action_bar.pack(fill="x", padx=4, pady=(2, 4))
        for attr, text, cmd in (
            ("btn_copy", "📋 Copy All", self.copy_all),
            ("btn_clear", "🧹 Clear Console", self.clear_logs),
            ("btn_export", "💾 Export", self.export_logs),
        ):
            btn = tk.Button(
                self.action_bar, text=text, font=FONT_BODY, bg=BG_SUBSURFACE, fg=TEXT_PRIMARY,
                activebackground=BG_HOVER, relief="flat", bd=0, padx=6, pady=2, cursor="hand2", command=cmd,
            )
            btn.pack(side="left", padx=2)
            setattr(self, attr, btn)

        self.var_autoscroll = tk.BooleanVar(value=True)
        self.var_autoscroll.trace_add("write", lambda *_: self._on_toggle_autoscroll())
        chk_scroll = tk.Checkbutton(
            self.action_bar, text="Auto-Scroll", variable=self.var_autoscroll, bg=BG_SURFACE,
            fg=TEXT_SECONDARY, selectcolor="#0A0C10", activebackground=BG_SURFACE, activeforeground=TEXT_PRIMARY,
            font=FONT_BODY, command=self._on_toggle_autoscroll,
        )
        chk_scroll.pack(side="right", padx=2)

    def _configure_tags(self) -> None:
        """Configure semantic colored tags for terminal syntax highlighting."""
        self.text_area.tag_config("info", foreground="#94A3B8")
        self.text_area.tag_config("health", foreground=STATUS_EMERALD)
        self.text_area.tag_config("ai_gate", foreground=ACCENT_CYAN)
        self.text_area.tag_config("warn", foreground=STATUS_AMBER)
        self.text_area.tag_config("crit", foreground=STATUS_CRIMSON)
        self.text_area.tag_config("success", foreground=STATUS_EMERALD)
        self.text_area.tag_config("time", foreground=STATUS_SLATE)

    def _on_toggle_autoscroll(self) -> None:
        self.auto_scroll = bool(self.var_autoscroll.get())

    def _on_filter_option_changed(self, selected: str) -> None:
        self.filter_level = selected.lower().replace(" ", "_")
        self._render_all()

    def set_subtab(self, subtab: str) -> None:
        """Switch between diagnostics (all) and errors sub-tab views."""
        self.active_subtab = subtab.lower()
        self._update_subtab_styling()
        self._render_all()

    def _update_subtab_styling(self) -> None:
        """Update button colors reflecting active sub-tab."""
        if self.active_subtab == "diagnostics":
            self.btn_subtab_diag.config(bg=BG_SURFACE, fg=ACCENT_CYAN)
            self.btn_subtab_err.config(bg=BG_SUBSURFACE, fg=TEXT_SECONDARY)
        else:
            self.btn_subtab_diag.config(bg=BG_SUBSURFACE, fg=TEXT_SECONDARY)
            self.btn_subtab_err.config(bg=BG_SURFACE, fg=STATUS_AMBER)

    def append_log(self, message: str, level: str = "info") -> None:
        """Append a new log entry to bounded buffer and render if it matches filter."""
        entry = {"time": time.strftime("[%H:%M:%S]"), "level": level.lower().strip(), "message": str(message)}
        self._entries.append(entry)
        if self._matches(entry):
            self._render_entry(entry)

    def clear_logs(self) -> None:
        """Clear all buffered logs and reset terminal display."""
        self._entries.clear()
        self.text_area.delete("1.0", tk.END)

    def copy_all(self) -> str:
        """Copy entire terminal content to system clipboard."""
        content = self.text_area.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(content)
        return content

    def export_logs(self, filepath: Optional[str] = None) -> bool:
        """Export current log content to a text or .log file."""
        if not filepath:
            try:
                from tkinter import filedialog
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".log", filetypes=[("Log files", "*.log"), ("All files", "*.*")]
                )
            except Exception:
                filepath = "smart_shutdown_export.log"
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", tk.END))
                return True
            except Exception:
                return False
        return False

    def filter_logs(self, query: str = "") -> None:
        """Filter log lines by search query in real time."""
        self.search_query = query.strip()
        self._render_all()

    def set_filter(self, level: str) -> None:
        """Programmatically set log level filter with canonical display labels."""
        key = level.lower().strip().replace(" ", "_")
        self.filter_level = key
        self.filter_var.set(self._FILTER_LABELS.get(key, level.title()))
        self._render_all()

    def _matches(self, entry: Dict[str, str]) -> bool:
        """Evaluate if entry matches sub-tab, filter level, and search criteria."""
        lvl = entry["level"]
        if self.active_subtab == "errors" and lvl not in ("warn", "crit", "error"):
            return False
        if self.filter_level != "all":
            if self.filter_level == "crit" and lvl not in ("crit", "error"):
                return False
            if self.filter_level != "crit" and lvl != self.filter_level:
                return False
        if self.search_query:
            q = self.search_query.lower()
            if q not in entry["message"].lower() and q not in lvl and q not in entry["time"]:
                return False
        return True

    def _render_entry(self, entry: Dict[str, str]) -> None:
        """Insert a single entry into the text area with semantic tagging."""
        tag = entry["level"]
        if tag not in ("info", "health", "ai_gate", "warn", "crit", "success"):
            tag = "crit" if tag == "error" else "info"
        self.text_area.insert(tk.END, entry["time"] + " ", "time")
        self.text_area.insert(tk.END, f"[{tag.upper()}] ", tag)
        self.text_area.insert(tk.END, entry["message"] + "\n", tag)
        if self.var_autoscroll.get():
            self.text_area.see(tk.END)

    def _render_all(self) -> None:
        """Re-render entire terminal text based on active filters."""
        self.text_area.delete("1.0", tk.END)
        for entry in self._entries:
            if self._matches(entry):
                self._render_entry(entry)
