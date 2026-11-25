# -*- coding: utf-8 -*-
"""
gui.components.settings_app_grid: Modular Application subtab 2-column grid,
master toolbar, category collapse, tri-state synchronization, and visibility helpers.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 200 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Any, List

from core.app_closer import is_running_under_test
from core.config import DEFAULT_APP_CLOSING_TARGETS, save_settings_config
from core.startup import enable_startup, disable_startup
from gui.components.app_catalog import APP_CATEGORIES, APP_DISPLAY_INFO
from gui.components.modern_checkbox import TriStateCheckbox
from gui.theme import (
    BG_BASE, BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_CARD,
    ACCENT_CYAN, STATUS_AMBER, STATUS_EMERALD,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_BADGE, FONT_BODY_BOLD,
)


def build_application_toolbar(view: Any) -> None:
    """Build Master Action Toolbar with Select/Deselect/Restore/Expand/Collapse and Counter."""
    view.app_toolbar = tk.Frame(view.cards_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=8, pady=5)
    left = tk.Frame(view.app_toolbar, bg=BG_SURFACE)
    left.pack(side="left")
    actions = [
        ("☑️ Select All", view._on_select_all_apps),
        ("⬜ Deselect All", view._on_deselect_all_apps),
        ("↩️ Restore Saved", view._on_restore_saved_apps),
        ("📂 Expand All", view._on_expand_all_categories),
        ("📁 Collapse All", view._on_collapse_all_categories),
    ]
    for text, cmd in actions:
        tk.Button(left, text=text, font=FONT_BADGE, bg=BG_SUBSURFACE, fg=TEXT_SECONDARY, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, relief="flat", bd=0, padx=8, pady=3, cursor="hand2", command=cmd).pack(side="left", padx=2)
    right = tk.Frame(view.app_toolbar, bg=BG_SURFACE)
    right.pack(side="right")
    badge = tk.Frame(right, bg=BG_SUBSURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=8, pady=3)
    badge.pack(side="right")
    view.lbl_app_counter = tk.Label(badge, text="0 / 0 Apps Enabled", font=FONT_BADGE, fg=ACCENT_CYAN, bg=BG_SUBSURFACE)
    view.lbl_app_counter.pack()


def build_application_cards(view: Any) -> None:
    """Create categorized collapsible application cards in a 2-column grid layout."""
    view._app_category_sections, view._category_headers = [], {}
    for cat_id, cat_label, app_keys in APP_CATEGORIES:
        cat_frame = tk.Frame(view.cards_frame, bg=BG_BASE)
        hdr = tk.Frame(cat_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=10, pady=6)
        hdr.pack(fill="x", padx=6, pady=(6, 2))
        left = tk.Frame(hdr, bg=BG_SURFACE, cursor="hand2")
        left.pack(side="left", fill="x", expand=True)
        chevron = tk.Label(left, text="▼", fg=ACCENT_CYAN, font=FONT_BODY_BOLD, bg=BG_SURFACE, cursor="hand2")
        chevron.pack(side="left", padx=(0, 6))
        title_lbl = tk.Label(left, text=cat_label, font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE, cursor="hand2")
        title_lbl.pack(side="left")
        cnt_lbl = tk.Label(left, text="(0/0)", font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SUBSURFACE, padx=6, pady=2)
        cnt_lbl.pack(side="left", padx=(8, 0))
        cb_cat = TriStateCheckbox(hdr, command=lambda _s, cid=cat_id: view._on_category_checkbox_clicked(cid), bg=BG_SURFACE)
        cb_cat.pack(side="right", padx=(6, 2))
        for w in (hdr, left, chevron, title_lbl, cnt_lbl):
            w.bind("<Button-1>", lambda _e, cid=cat_id: view._toggle_category_collapse(cid))
        grid_frame = tk.Frame(cat_frame, bg=BG_BASE)
        grid_frame.pack(fill="x", padx=2, pady=(3, 0))
        grid_frame.columnconfigure(0, weight=1, uniform="app_col")
        grid_frame.columnconfigure(1, weight=1, uniform="app_col")
        view._category_headers[cat_id] = (chevron, cb_cat, cnt_lbl, grid_frame)
        app_cards = build_category_app_cards(view, grid_frame, cat_id, app_keys)
        view._app_category_sections.append((cat_id, cat_label, cat_frame, grid_frame, app_cards))


def build_category_app_cards(view: Any, grid_frame: tk.Frame, cat_id: str, app_keys: List[str]) -> List[Any]:
    """Construct individual modern application cards for a category."""
    app_cards = []
    for name in app_keys:
        if name not in APP_DISPLAY_INFO or (name != "AntiGravity" and name not in view.var_app_targets):
            continue
        title, desc, kw = APP_DISPLAY_INFO[name]
        var = view.var_close_antigravity if name == "AntiGravity" else view.var_app_targets[name]
        cb = (lambda cid=cat_id: view._on_app_toggled(cid, view._on_antigravity_toggle)) if name == "AntiGravity" else (lambda cid=cat_id: view._on_app_toggled(cid))
        card = view._create_app_card(grid_frame, title, desc, var, cb)
        app_cards.append((card, title, desc, kw, var, cb))
    return app_cards


def apply_category_collapse(view: Any, cat_id: str) -> None:
    """Apply collapsed or expanded geometry state to a category section."""
    if cat_id not in view._category_headers:
        return
    chevron, _, _, grid_frame = view._category_headers[cat_id]
    if view._category_collapsed.get(cat_id, False):
        chevron.config(text="▶", fg=TEXT_SECONDARY)
        grid_frame.pack_forget()
    else:
        chevron.config(text="▼", fg=ACCENT_CYAN)
        grid_frame.pack(fill="x", padx=2, pady=(3, 0))


def update_category_state(view: Any, cat_id: str) -> None:
    """Update tri-state checkbox and count chip for a single category."""
    if cat_id not in view._category_headers:
        return
    _, cb_cat, lbl_count, _ = view._category_headers[cat_id]
    section = next((s for s in view._app_category_sections if s[0] == cat_id), None)
    if not section:
        return
    total = len(section[4])
    checked = sum(1 for _, _, _, _, var, _ in section[4] if var.get())
    if checked == total and total > 0:
        cb_cat.set_state(TriStateCheckbox.STATE_CHECKED)
        lbl_count.config(text=f"({checked}/{total})", fg=STATUS_EMERALD, bg="#0D2E24")
    elif checked > 0:
        cb_cat.set_state(TriStateCheckbox.STATE_PARTIAL)
        lbl_count.config(text=f"({checked}/{total})", fg=STATUS_AMBER, bg="#2D2210")
    else:
        cb_cat.set_state(TriStateCheckbox.STATE_UNCHECKED)
        lbl_count.config(text=f"({checked}/{total})", fg=TEXT_SECONDARY, bg=BG_SUBSURFACE)


def update_master_app_counter(view: Any) -> None:
    """Update master enabled-apps counter badge on the Application toolbar."""
    total_apps = sum(len(c[4]) for c in view._app_category_sections)
    total_checked = sum(sum(1 for _, _, _, _, var, _ in c[4] if var.get()) for c in view._app_category_sections)
    if hasattr(view, "lbl_app_counter"):
        view.lbl_app_counter.config(text=f"[{total_checked} / {total_apps} Apps Enabled]")


def toggle_category_checkbox(view: Any, cat_id: str) -> None:
    """Toggle all applications in a category on category checkbox click."""
    section = next((s for s in view._app_category_sections if s[0] == cat_id), None)
    if not section:
        return
    target_state = not all(var.get() for _, _, _, _, var, _ in section[4])
    for _, _, _, _, var, _ in section[4]:
        var.set(target_state)
    if cat_id == "developer" and "AntiGravity" in view.var_app_targets:
        view.var_close_antigravity.set(view.var_app_targets["AntiGravity"].get())
    update_category_state(view, cat_id)
    update_master_app_counter(view)


def sync_app_targets_state(view: Any, saved_only: bool = False, select_all: bool | None = None) -> None:
    """Apply bulk target updates (select_all, restore saved, or reset factory defaults)."""
    if select_all is not None:
        view.var_close_antigravity.set(select_all)
        for var in view.var_app_targets.values():
            var.set(select_all)
    elif saved_only:
        view.var_close_antigravity.set(view._saved_close_antigravity)
        for k, v in view._saved_app_targets.items():
            if k in view.var_app_targets:
                view.var_app_targets[k].set(v)
        if "AntiGravity" in view.var_app_targets:
            view.var_app_targets["AntiGravity"].set(view._saved_close_antigravity)
    else:
        view.var_close_antigravity.set(True)
        for k, v in DEFAULT_APP_CLOSING_TARGETS.items():
            if k in view.var_app_targets:
                view.var_app_targets[k].set(bool(v))
        if "AntiGravity" in view.var_app_targets:
            view.var_app_targets["AntiGravity"].set(True)
    view._update_all_category_states()
    update_master_app_counter(view)


def refresh_cards_visibility(view: Any) -> None:
    """Filter and reflow subtab cards and 2-column collapsible application sections."""
    query = view.search_query
    for card, subtab, keywords in view._cards:
        match = (query in keywords.lower()) if query else (subtab == view.active_subtab)
        card.pack(fill="x", padx=6, pady=4) if match else card.pack_forget()
    show_apps = (view.active_subtab == "application") or bool(query)
    matching_apps = 0
    if hasattr(view, "app_toolbar"):
        view.app_toolbar.pack_forget()
    for cat_id, cat_label, cat_frame, grid_frame, app_cards in view._app_category_sections:
        visible = [c for c, t, d, kw, _, _ in app_cards if not query or query in f"{t} {d} {kw} {cat_label}".lower()]
        for c, *_ in app_cards:
            if c not in visible:
                c.grid_forget()
        if visible and show_apps:
            matching_apps += len(visible)
            cat_frame.pack(fill="x", padx=4, pady=(2, 6))
            if query:
                if cat_id in view._category_headers:
                    view._category_headers[cat_id][0].config(text="▼", fg=ACCENT_CYAN)
                grid_frame.pack(fill="x", padx=2, pady=(3, 0))
            else:
                apply_category_collapse(view, cat_id)
            for idx, card in enumerate(visible):
                card.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=4, pady=3)
        else:
            cat_frame.pack_forget()
    if hasattr(view, "app_toolbar") and show_apps and (view.active_subtab == "application" or matching_apps > 0):
        children = [w for w in view.cards_frame.winfo_children() if w != view.app_toolbar and w.winfo_manager() == "pack"]
        view.app_toolbar.pack(fill="x", padx=4, pady=(2, 4), before=children[0] if children else None)


def bind_slider_label(var: Any, lbl_val: tk.Label, unit: str, is_double: bool) -> None:
    """Keep numeric readout label synchronized whenever slider variable changes programmatically."""
    def _sync(*_args: Any) -> None:
        try:
            if lbl_val.winfo_exists():
                val = var.get()
                lbl_val.config(text=f"{float(val):.1f}{unit}" if is_double else f"{int(float(val))}{unit}")
        except (tk.TclError, ValueError):
            pass
    var.trace_add("write", _sync)


def handle_startup_toggle(view: Any) -> None:
    """Apply Windows Startup toggle safely while guarding automated test runs."""
    if is_running_under_test():
        return
    start_win = bool(view.var_startup.get())
    mini_hud = bool(view.var_mini_hud_startup.get())
    if getattr(view, "config", None) is not None:
        view.config.start_with_windows = start_win
        view.config.mini_hud_on_startup = mini_hud
        save_settings_config(view.config)
    if start_win:
        enable_startup(
            countdown=int(view.var_timer.get() * 60),
            idle_buffer=int(view.var_inactivity.get() * 60),
            mini_hud=mini_hud,
        )
    else:
        disable_startup()
