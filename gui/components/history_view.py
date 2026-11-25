# -*- coding: utf-8 -*-
"""
gui.components.history_view: Tab 4 Event History and Audit Timeline Component.
Houses single-row 5 sub-tabs, search bar, date filter, KPI stat chips,
scrollable timeline card list, clear action, and CSV export.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 350 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import io
import csv
import time
import tkinter as tk
from typing import Optional, List, Dict, Any

from gui.theme import (
    BG_BASE, BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED, BORDER_CARD,
    ACCENT_CYAN, STATUS_EMERALD, STATUS_AMBER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_BADGE, FONT_BODY, FONT_BODY_BOLD,
)


class HistoryView(tk.Frame):
    """Tab 4 History View: 5 sub-tabs, search, date filter, KPIs, cards, CSV export."""

    SUBTABS = [
        ("power", "⚡ Power"), ("blockers", "🛑 Blockers"),
        ("snoozes", "💤 Snoozes"), ("dry_run", "🧪 Dry-Run"), ("sessions", "🖥️ Sessions"),
    ]

    def __init__(self, parent: tk.Widget, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.active_subtab = "power"
        self.date_filter = "All Dates"
        self.search_query = ""
        self._events: List[Dict[str, Any]] = []
        self._subtab_buttons: Dict[str, tk.Button] = {}
        self._build_ui()
        self.update_kpi_display()

    def _build_ui(self) -> None:
        """Construct single-row toolbar, KPI chips, scrollable cards, and action bar."""
        self._build_toolbar()
        self._build_kpi_row()
        self._build_scroll_viewport()
        self._build_action_bar()

    def _build_toolbar(self) -> None:
        """Construct single-row sub-navigation, search box, and date filter dropdown."""
        self.toolbar = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.toolbar.pack(fill="x", padx=4, pady=(2, 4))

        left_subtabs = tk.Frame(self.toolbar, bg=BG_SURFACE)
        left_subtabs.pack(side="left")
        for tid, label in self.SUBTABS:
            btn = tk.Button(
                left_subtabs, text=label, font=FONT_BADGE,
                bg="#0D2535" if tid == self.active_subtab else BG_SUBSURFACE,
                fg=ACCENT_CYAN if tid == self.active_subtab else TEXT_SECONDARY,
                activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
                relief="flat", bd=0, padx=6, pady=3, cursor="hand2",
                command=lambda t=tid: self.set_subtab(t),
            )
            btn.pack(side="left", padx=1)
            self._subtab_buttons[tid] = btn

        right_controls = tk.Frame(self.toolbar, bg=BG_SURFACE)
        right_controls.pack(side="right")
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(
            right_controls, textvariable=self.search_var, bg=BG_SUBSURFACE, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, font=FONT_BODY, relief="flat", highlightthickness=1,
            highlightbackground=BORDER_MUTED, width=16,
        )
        self.entry_search.pack(side="left", padx=(0, 4))
        self.search_var.trace_add("write", lambda *_: self.filter_history(self.search_var.get()))

        self.date_var = tk.StringVar(value="All Dates")
        self.opt_date = tk.OptionMenu(
            right_controls, self.date_var, "All Dates", "Today", "Past 7 Days", "Past 30 Days",
            command=self._on_date_changed,
        )
        self.opt_date.config(
            bg=BG_SUBSURFACE, fg=TEXT_SECONDARY, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
            font=FONT_BADGE, highlightthickness=1, highlightbackground=BORDER_MUTED, bd=0, relief="flat", cursor="hand2",
        )
        self.opt_date["menu"].config(bg=BG_SURFACE, fg=TEXT_PRIMARY, activebackground=BG_HOVER, activeforeground=ACCENT_CYAN)
        self.opt_date.pack(side="left")

    def _build_kpi_row(self) -> None:
        """Construct 3-column summary KPI stat chips."""
        self.kpi_row = tk.Frame(self, bg=BG_BASE)
        self.kpi_row.pack(fill="x", padx=4, pady=(2, 4))
        for c in range(3):
            self.kpi_row.columnconfigure(c, weight=1)
        self.lbl_kpi_reboots = self._create_kpi_chip(self.kpi_row, 0, "Total Reboots: 0", STATUS_AMBER)
        self.lbl_kpi_pauses = self._create_kpi_chip(self.kpi_row, 1, "User Pauses: 0", ACCENT_CYAN)
        self.lbl_kpi_shutdowns = self._create_kpi_chip(self.kpi_row, 2, "Clean Shutdowns: 0", STATUS_EMERALD)

    def _build_scroll_viewport(self) -> None:
        """Construct scrollable canvas viewport with hover-scoped mousewheel."""
        self.canvas_container = tk.Frame(self, bg=BG_BASE, highlightbackground=BORDER_MUTED, highlightthickness=1)
        self.canvas_container.pack(fill="both", expand=True, padx=4, pady=2)
        self.canvas = tk.Canvas(self.canvas_container, bg=BG_BASE, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview, bg=BG_SURFACE)
        self.cards_frame = tk.Frame(self.canvas, bg=BG_BASE)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas_container.bind("<Enter>", self._bind_mousewheel, add="+")
        self.canvas_container.bind("<Leave>", self._unbind_mousewheel, add="+")
        self.canvas_container.bind("<Destroy>", self._unbind_mousewheel, add="+")
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

    def _build_action_bar(self) -> None:
        """Construct bottom action bar with Clear History and Export CSV."""
        self.action_bar = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.action_bar.pack(fill="x", padx=4, pady=(2, 4))
        self.btn_clear = tk.Button(
            self.action_bar, text="🧹 Clear History", font=FONT_BODY_BOLD, bg=BG_SUBSURFACE, fg=STATUS_AMBER,
            activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, relief="flat", bd=0, padx=10, pady=4,
            cursor="hand2", command=self.clear_history,
        )
        self.btn_clear.pack(side="left", padx=4)
        self.btn_export_csv = tk.Button(
            self.action_bar, text="📤 Export CSV", font=FONT_BODY_BOLD, bg="#0D2535", fg=ACCENT_CYAN,
            activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, relief="flat", bd=0, padx=12, pady=4,
            cursor="hand2", command=self._on_export_click,
        )
        self.btn_export_csv.pack(side="right", padx=4)

    def _create_kpi_chip(self, parent: tk.Widget, col: int, title: str, color: str) -> tk.Label:
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=8, pady=4)
        card.grid(row=0, column=col, padx=3, sticky="ew")
        lbl = tk.Label(card, text=title, font=FONT_BADGE, fg=color, bg=BG_SURFACE)
        lbl.pack(anchor="center")
        return lbl

    def _bind_mousewheel(self, _event=None) -> None:
        try:
            if self.canvas.winfo_exists():
                self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        except tk.TclError:
            pass

    def _unbind_mousewheel(self, _event=None) -> None:
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass

    def _on_mousewheel(self, event) -> None:
        try:
            if self.canvas.winfo_exists() and self.cards_frame.winfo_exists():
                delta = -1 if event.delta < 0 else 1
                self.canvas.yview_scroll(-delta, "units")
        except tk.TclError:
            pass

    def _on_date_changed(self, val: str) -> None:
        self.date_filter = val
        self._render_cards()

    def _on_export_click(self) -> None:
        csv_data = self.export_csv()
        try:
            self.clipboard_clear()
            self.clipboard_append(csv_data)
        except Exception:
            pass

    def update_kpi_display(self) -> None:
        """Recalculate and update the 3 summary KPI chips."""
        reboots = sum(1 for e in self._events if any(k in e["title"].lower() or k in e.get("event_type", "").lower() for k in ("reboot", "restart")))
        pauses = sum(1 for e in self._events if any(k in e["title"].lower() or k in e.get("event_type", "").lower() for k in ("pause", "snooze")))
        shutdowns = sum(1 for e in self._events if any(k in e["title"].lower() or k in e.get("event_type", "").lower() for k in ("shutdown", "clean")))
        self.lbl_kpi_reboots.config(text=f"Total Reboots: {reboots}")
        self.lbl_kpi_pauses.config(text=f"User Pauses: {pauses}")
        self.lbl_kpi_shutdowns.config(text=f"Clean Shutdowns: {shutdowns}")

    def add_event(self, event_type: str, title: str, timestamp: str, reason: str) -> None:
        """Append historical event with epoch timestamp, update KPIs, and refresh cards."""
        self._events.append({
            "event_type": event_type,
            "title": title,
            "timestamp": timestamp,
            "reason": reason,
            "_epoch": time.time(),
        })
        self.update_kpi_display()
        self._render_cards()

    def set_subtab(self, subtab_name: str) -> None:
        """Switch active sub-tab category and refresh timeline."""
        subtab_lower = subtab_name.lower()
        self.active_subtab = subtab_lower
        for tid, btn in self._subtab_buttons.items():
            active = (tid == subtab_lower)
            btn.config(
                bg="#0D2535" if active else BG_SUBSURFACE,
                fg=ACCENT_CYAN if active else TEXT_SECONDARY,
                highlightbackground=ACCENT_CYAN if active else BORDER_MUTED,
            )
        self._render_cards()

    def filter_history(self, query: str) -> None:
        """Filter timeline entries in real-time by search query string."""
        self.search_query = query.strip().lower()
        self._render_cards()

    def clear_history(self) -> None:
        """Clear all historical events and reset counters."""
        self._events.clear()
        self.update_kpi_display()
        self._render_cards()

    def export_csv(self, file_path: Optional[str] = None) -> str:
        """Export timeline records to CSV format string or optional file path."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["timestamp", "event_type", "title", "reason"])
        for ev in self._events:
            writer.writerow([ev.get("timestamp", ""), ev.get("event_type", ""), ev.get("title", ""), ev.get("reason", "")])
        csv_text = output.getvalue()
        if file_path:
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(csv_text)
        return csv_text

    def _matches_date_filter(self, ev: Dict[str, Any], ts: str) -> bool:
        """Evaluate date filter against event epoch with string fallback."""
        if self.date_filter == "All Dates":
            return True
        epoch = ev.get("_epoch")
        age = (time.time() - float(epoch)) if epoch is not None else None
        if self.date_filter == "Today":
            if "today" in ts or "just now" in ts:
                return True
            return age is not None and age < 86400
        if self.date_filter == "Past 7 Days":
            return True if age is None else (age <= 7 * 86400)
        if self.date_filter == "Past 30 Days":
            return True if age is None else (age <= 30 * 86400)
        return True

    def _matches_filter(self, ev: Dict[str, Any]) -> bool:
        etype = str(ev.get("event_type", "")).lower()
        title = str(ev.get("title", "")).lower()
        reason = str(ev.get("reason", "")).lower()
        ts = str(ev.get("timestamp", "")).lower()
        if self.active_subtab != "all":
            mapping = {
                "power": ("power", "shutdown", "reboot", "restart"),
                "blockers": ("block", "inhibit"),
                "snoozes": ("snooze", "pause"),
                "dry_run": ("dry", "simul", "demo"),
                "sessions": ("session", "start", "exit", "close"),
            }
            keywords = mapping.get(self.active_subtab, (self.active_subtab,))
            if not any(k in etype or k in title for k in keywords):
                return False
        if self.search_query and not any(self.search_query in x for x in (title, reason, etype, ts)):
            return False
        return self._matches_date_filter(ev, ts)

    def _render_cards(self) -> None:
        """Render matching timeline card widgets inside cards_frame."""
        for child in self.cards_frame.winfo_children():
            child.destroy()
        matching = [e for e in self._events if self._matches_filter(e)]
        if not matching:
            tk.Label(self.cards_frame, text="No events match current filter or history is empty.", font=FONT_BODY, fg=TEXT_MUTED, bg=BG_BASE, pady=20).pack(fill="x")
            return
        for ev in reversed(matching):
            self._render_single_card(ev)

    def _render_single_card(self, ev: Dict[str, Any]) -> None:
        """Render an individual event timeline card."""
        card = tk.Frame(self.cards_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=10, pady=6)
        card.pack(fill="x", padx=4, pady=3)
        top_row = tk.Frame(card, bg=BG_SURFACE)
        top_row.pack(fill="x")

        icon = "⚡"
        etype = str(ev.get("event_type", "")).lower()
        if "block" in etype:
            icon = "🛑"
        elif "snooze" in etype or "pause" in etype:
            icon = "💤"
        elif "dry" in etype or "simul" in etype:
            icon = "🧪"
        elif "session" in etype:
            icon = "🖥️"

        tk.Label(top_row, text=f"{icon} {ev.get('title', '')}", font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE).pack(side="left")
        tk.Label(top_row, text=ev.get("timestamp", ""), font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SURFACE).pack(side="right")

        reason_text = ev.get("reason", "")
        if reason_text:
            bot_row = tk.Frame(card, bg=BG_SURFACE)
            bot_row.pack(fill="x", pady=(3, 0))
            chip_frame = tk.Frame(bot_row, bg=BG_SUBSURFACE, padx=6, pady=2)
            chip_frame.pack(side="left")
            tk.Label(chip_frame, text=f"Reason: {reason_text}", font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SUBSURFACE).pack()
