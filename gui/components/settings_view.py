# -*- coding: utf-8 -*-
"""
gui.components.settings_view: Tab 5 Settings Configuration Deck Component.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 400 lines, < 24 KB).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Optional, Callable, List, Tuple, Any, Dict

from core.config import SettingsConfig, DEFAULT_APP_CLOSING_TARGETS
from core.models import DEFAULT_SIMULATION_SECONDS
from core.startup import is_startup_enabled
from gui.components.app_catalog import APP_CATEGORIES
from gui.components.modern_checkbox import ModernCheckbox, TriStateCheckbox
from gui.components import settings_app_grid as app_grid
from gui.theme import (
    BG_BASE, BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED, BORDER_CARD,
    ACCENT_CYAN, STATUS_AMBER, STATUS_RED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_BADGE, FONT_BODY, FONT_BODY_BOLD,
)


class SettingsView(tk.Frame):
    """Tab 5 Settings View with 4 sub-tabs, collapsible category grid, and master controls."""

    SUBTABS = [("general", "⚙️ General"), ("application", "📱 Application"), ("limits", "🎯 Limits"), ("actions", "⚡ Actions")]

    def __init__(self, parent: tk.Widget, config: Optional[SettingsConfig] = None, on_save: Optional[Callable[[SettingsConfig], None]] = None, on_mode_change: Optional[Callable[[str], None]] = None, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.config = config or SettingsConfig()
        self.config.clamp()
        self.on_save_callback, self.on_mode_change = on_save, on_mode_change
        self.active_subtab, self.search_query = "general", ""
        self._cards: List[Tuple[tk.Frame, str, str]] = []
        self._app_category_sections: List[Tuple[str, str, tk.Frame, tk.Frame, List[Any]]] = []
        self._category_headers: Dict[str, Tuple[tk.Label, TriStateCheckbox, tk.Label, tk.Frame]] = {}
        self._category_collapsed: Dict[str, bool] = {c[0]: False for c in APP_CATEGORIES}
        self._subtab_buttons: Dict[str, tk.Button] = {}
        self._mode_buttons: Dict[str, tk.Button] = {}
        self._syncing_ag = False
        self._init_variables()
        self._build_ui()
        self.load_config(self.config)

    def _init_variables(self) -> None:
        """Initialize Tkinter state variables for all settings."""
        c = self.config
        self.var_startup = tk.BooleanVar(value=is_startup_enabled())
        self.var_minimize_tray = tk.BooleanVar(value=getattr(c, "minimize_to_tray", True))
        self.var_mini_hud_startup = tk.BooleanVar(value=getattr(c, "mini_hud_on_startup", True))
        self.var_inactivity = tk.IntVar(value=max(1, c.user_inactivity_sec // 60))
        self.var_timer = tk.IntVar(value=c.master_shutdown_timer_min)
        self.var_sim_timer = tk.IntVar(value=getattr(c, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS))
        self.var_cpu = tk.DoubleVar(value=getattr(c, "cpu_threshold_pct", 15.0))
        self.var_net = tk.DoubleVar(value=getattr(c, "network_threshold_kb", 50.0))
        self.var_audio = tk.BooleanVar(value=getattr(c, "audio_inhibit_enabled", True))
        self.var_target_action = tk.StringVar(value=getattr(c, "target_action", "Shutdown"))
        self.var_exec_mode = tk.StringVar(value=getattr(c, "execution_mode", "Live"))
        self.var_close_antigravity = tk.BooleanVar(value=getattr(c, "close_antigravity", True))
        t = getattr(c, "app_closing_targets", {}) or {}
        self.var_app_targets = {k: tk.BooleanVar(value=bool(t.get(k, v))) for k, v in DEFAULT_APP_CLOSING_TARGETS.items()}
        if "AntiGravity" in self.var_app_targets:
            self.var_app_targets["AntiGravity"].set(self.var_close_antigravity.get())
            self.var_app_targets["AntiGravity"].trace_add("write", lambda *_: self._sync_antigravity(True))
        self.var_close_antigravity.trace_add("write", lambda *_: self._sync_antigravity(False))
        self._saved_close_antigravity = self.var_close_antigravity.get()
        self._saved_app_targets = {k: v.get() for k, v in self.var_app_targets.items()}

    def _build_ui(self) -> None:
        """Construct toolbar, viewport, application toolbar, settings cards, and footer."""
        self._build_top_toolbar()
        self._build_canvas_viewport()
        self._build_application_toolbar()
        self._build_general_cards()
        self._build_application_cards()
        self._build_limits_cards()
        self._build_actions_cards()
        self._build_footer()
        self._refresh_cards_visibility()

    def _build_top_toolbar(self) -> None:
        self.toolbar = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.toolbar.pack(fill="x", padx=4, pady=(2, 4))
        left = tk.Frame(self.toolbar, bg=BG_SURFACE)
        left.pack(side="left")
        for tid, label in self.SUBTABS:
            act = (tid == self.active_subtab)
            btn = tk.Button(left, text=label, font=FONT_BADGE, relief="flat", bd=0, padx=8, pady=3, cursor="hand2", bg="#0D2535" if act else BG_SUBSURFACE, fg=ACCENT_CYAN if act else TEXT_SECONDARY, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, command=lambda t=tid: self.set_subtab(t))
            btn.pack(side="left", padx=1)
            self._subtab_buttons[tid] = btn
        right = tk.Frame(self.toolbar, bg=BG_SURFACE)
        right.pack(side="right")
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(right, textvariable=self.search_var, bg=BG_SUBSURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, font=FONT_BODY, relief="flat", highlightthickness=1, highlightbackground=BORDER_MUTED, width=18)
        self.entry_search.pack(side="left", padx=2)
        self.search_var.trace_add("write", lambda *_: self.filter_settings(self.search_var.get()))

    def _build_canvas_viewport(self) -> None:
        self.canvas_container = tk.Frame(self, bg=BG_BASE, highlightbackground=BORDER_MUTED, highlightthickness=1)
        self.canvas_container.pack(fill="both", expand=True, padx=4, pady=2)
        self.canvas = tk.Canvas(self.canvas_container, bg=BG_BASE, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview, bg=BG_SURFACE)
        self.cards_frame = tk.Frame(self.canvas, bg=BG_BASE)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas_container.bind("<Enter>", self._bind_mousewheel, add="+")
        self.canvas_container.bind("<Leave>", self._unbind_mousewheel, add="+")
        self.canvas_container.bind("<Destroy>", self._unbind_mousewheel, add="+")
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

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
                self.canvas.yview_scroll(-(-1 if event.delta < 0 else 1), "units")
        except tk.TclError:
            pass

    def _build_application_toolbar(self) -> None:
        app_grid.build_application_toolbar(self)

    def _build_footer(self) -> None:
        self.footer = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED, highlightthickness=1, padx=6, pady=4)
        self.footer.pack(fill="x", padx=4, pady=(2, 4))
        self.btn_reset = tk.Button(self.footer, text="🔄 Reset Defaults", font=FONT_BODY_BOLD, bg=BG_SUBSURFACE, fg=STATUS_AMBER, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, relief="flat", bd=0, padx=12, pady=4, cursor="hand2", command=self._on_reset_clicked)
        self.btn_reset.pack(side="left", padx=4)
        self.btn_save = tk.Button(self.footer, text="💾 Save Changes", font=FONT_BODY_BOLD, bg="#0D2535", fg=ACCENT_CYAN, activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY, relief="flat", bd=0, padx=16, pady=4, cursor="hand2", command=self._on_save_clicked)
        self.btn_save.pack(side="right", padx=4)

    def _build_general_cards(self) -> None:
        for title, desc, var, kw, cb in (
            ("Start Smart Shutdown automatically with Windows", "Creates startup shortcut to monitor and protect workstation on boot.", self.var_startup, "startup boot windows run autostart", self._on_startup_toggle),
            ("Minimize to System Tray on close [X]", "Keep Smart Shutdown active in system tray when main window close is pressed.", self.var_minimize_tray, "tray minimize close background notification", None),
            ("Show floating Mini HUD on startup", "Launches directly into the compact topmost overlay HUD on boot.", self.var_mini_hud_startup, "mini hud overlay floating topmost startup", None),
        ):
            self._add_toggle_card("general", title, desc, var, kw, on_toggle=cb)

    def _build_application_cards(self) -> None:
        app_grid.build_application_cards(self)

    def _build_category_app_cards(self, grid_frame: tk.Frame, cat_id: str, app_keys: List[str]) -> List[Any]:
        return app_grid.build_category_app_cards(self, grid_frame, cat_id, app_keys)

    def _create_toggle_card(self, parent: tk.Widget, title: str, desc: str, var: tk.BooleanVar, on_toggle: Optional[Callable[[], None]] = None, px: int = 10, py: int = 6) -> tk.Frame:
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=px, pady=py)
        row = tk.Frame(card, bg=BG_SURFACE)
        row.pack(fill="x")
        lbl = tk.Frame(row, bg=BG_SURFACE)
        lbl.pack(side="left", fill="x", expand=True)
        tk.Label(lbl, text=title, font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE).pack(anchor="w")
        tk.Label(lbl, text=desc, font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SURFACE).pack(anchor="w", pady=(2, 0))
        ModernCheckbox(row, variable=var, command=on_toggle, bg=BG_SURFACE).pack(side="right", padx=4)
        return card

    def _create_app_card(self, parent: tk.Widget, title: str, desc: str, var: tk.BooleanVar, on_toggle: Optional[Callable[[], None]] = None) -> tk.Frame:
        return self._create_toggle_card(parent, title, desc, var, on_toggle, px=10, py=6)

    def _add_toggle_card(self, subtab: str, title: str, desc: str, var: tk.BooleanVar, keywords: str, on_toggle: Optional[Callable[[], None]] = None) -> None:
        self._cards.append((self._create_toggle_card(self.cards_frame, title, desc, var, on_toggle, px=12, py=8), subtab, f"{title} {desc} {keywords}"))

    def _on_app_toggled(self, cat_id: str, orig_cb: Optional[Callable[[], None]] = None) -> None:
        if orig_cb:
            orig_cb()
        app_grid.update_category_state(self, cat_id)
        app_grid.update_master_app_counter(self)

    def _on_category_checkbox_clicked(self, cat_id: str) -> None:
        app_grid.toggle_category_checkbox(self, cat_id)

    def _set_all_apps_selected(self, selected: bool) -> None:
        app_grid.sync_app_targets_state(self, select_all=selected)

    def _on_select_all_apps(self) -> None:
        app_grid.sync_app_targets_state(self, select_all=True)

    def _on_deselect_all_apps(self) -> None:
        app_grid.sync_app_targets_state(self, select_all=False)

    def _on_restore_saved_apps(self) -> None:
        app_grid.sync_app_targets_state(self, saved_only=True)

    def _on_reset_app_defaults(self) -> None:
        app_grid.sync_app_targets_state(self, saved_only=False)

    def _toggle_category_collapse(self, cat_id: str) -> None:
        self._category_collapsed[cat_id] = not self._category_collapsed.get(cat_id, False)
        app_grid.apply_category_collapse(self, cat_id)

    def _apply_category_collapse(self, cat_id: str) -> None:
        app_grid.apply_category_collapse(self, cat_id)

    def _set_all_categories_collapsed(self, collapsed: bool) -> None:
        for cat_id in self._category_collapsed:
            self._category_collapsed[cat_id] = collapsed
            app_grid.apply_category_collapse(self, cat_id)

    def _on_expand_all_categories(self) -> None:
        self._set_all_categories_collapsed(False)

    def _on_collapse_all_categories(self) -> None:
        self._set_all_categories_collapsed(True)

    def _update_category_state(self, cat_id: str) -> None:
        app_grid.update_category_state(self, cat_id)

    def _update_all_category_states(self) -> None:
        for cat_id, *_ in self._app_category_sections:
            app_grid.update_category_state(self, cat_id)

    def _update_master_app_counter(self) -> None:
        app_grid.update_master_app_counter(self)

    def _sync_antigravity(self, from_target: bool = False) -> None:
        if self._syncing_ag:
            return
        self._syncing_ag = True
        try:
            ag = self.var_app_targets.get("AntiGravity")
            if from_target and ag is not None and self.var_close_antigravity.get() != ag.get():
                self.var_close_antigravity.set(ag.get())
            elif not from_target and ag is not None and ag.get() != self.var_close_antigravity.get():
                ag.set(self.var_close_antigravity.get())
            app_grid.update_category_state(self, "developer")
            app_grid.update_master_app_counter(self)
        finally:
            self._syncing_ag = False

    def _on_antigravity_toggle(self) -> None:
        self._sync_antigravity(False)

    def _build_limits_cards(self) -> None:
        """Create Limits sub-tab sliders (keeping 1..120m inactivity slider) and audio toggle."""
        for title, var, lo, hi, unit, desc, kw, is_dbl in (
            ("Inactivity Timeout (minutes)", self.var_inactivity, 1, 120, "m", "Time without user mouse or keyboard input before countdown triggers.", "inactivity timeout idle input user minutes", False),
            ("Master Countdown Timer (minutes)", self.var_timer, 1, 60, "m", "Duration of grace countdown before target power action executes.", "master countdown timer shutdown minutes duration", False),
            ("Simulation Duration (seconds)", self.var_sim_timer, 10, 900, "s", "Dry-run countdown duration in Simulation mode (default: 300s / 5m).", "simulation duration timer dry run seconds", False),
            ("CPU Activity Threshold (%)", self.var_cpu, 1, 100, "%", "Inhibits shutdown if background CPU utilization exceeds this value.", "cpu processor activity threshold busy percent", True),
            ("Network Throughput Threshold (KB/s)", self.var_net, 0, 1000, " KB/s", "Inhibits shutdown if download throughput exceeds this speed.", "network throughput download transfer speed kb threshold", True),
        ):
            self._add_slider_card("limits", title, var, lo, hi, unit, desc, kw, is_double=is_dbl)
        self._add_toggle_card("limits", "WASAPI Audio Stream Inhibit", "Inhibit shutdown while Windows audio streams or media players are playing.", self.var_audio, "audio sound media wasapi music video inhibit")

    def _build_actions_cards(self) -> None:
        """Create target power action and coordinator execution mode cards."""
        card_act = tk.Frame(self.cards_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=12, pady=8)
        tk.Label(card_act, text="⚡ Target Power Action", font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE).pack(anchor="w")
        tk.Label(card_act, text="Select power operation dispatched when timer reaches zero.", font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SURFACE).pack(anchor="w", pady=(2, 6))
        radios = tk.Frame(card_act, bg=BG_SURFACE)
        radios.pack(fill="x")
        for a in ("Shutdown", "Hibernate", "Sleep", "Lock Screen"):
            tk.Radiobutton(radios, text=a, variable=self.var_target_action, value=a, bg=BG_SURFACE, fg=TEXT_PRIMARY, selectcolor=BG_SUBSURFACE, activebackground=BG_SURFACE, activeforeground=ACCENT_CYAN, font=FONT_BODY, cursor="hand2").pack(side="left", padx=8)
        self._cards.append((card_act, "actions", "target power action shutdown hibernate sleep lock screen"))

        card_mode = tk.Frame(self.cards_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=12, pady=8)
        tk.Label(card_mode, text="🧪 Coordinator Execution Mode", font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE).pack(anchor="w")
        tk.Label(card_mode, text="Toggle between live system shutdown, 30s demo, or 5m simulation.", font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SURFACE).pack(anchor="w", pady=(2, 6))
        modes = tk.Frame(card_mode, bg=BG_SURFACE)
        modes.pack(fill="x")
        for m_val, m_lbl in (("Live", "⚡ Live"), ("Demo (30s)", "⚡ Demo (30s)"), ("Simulation", "🛡️ Simulation")):
            btn = tk.Button(modes, text=m_lbl, font=FONT_BADGE, relief="flat", bd=0, padx=10, pady=4, cursor="hand2", command=lambda v=m_val: self.set_mode(v))
            btn.pack(side="left", padx=4)
            self._mode_buttons[m_val] = btn
        self._cards.append((card_mode, "actions", "mode switcher coordinator execution live demo simulation"))

    def _add_slider_card(self, subtab: str, title: str, var: Any, from_: int, to_: int, unit: str, desc: str, keywords: str, is_double: bool = False) -> None:
        card = tk.Frame(self.cards_frame, bg=BG_SURFACE, highlightbackground=BORDER_CARD, highlightthickness=1, padx=12, pady=8)
        row_top = tk.Frame(card, bg=BG_SURFACE)
        row_top.pack(fill="x")
        tk.Label(row_top, text=title, font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE).pack(side="left")
        lbl_val = tk.Label(row_top, text=f"{var.get():.1f}{unit}" if is_double else f"{int(var.get())}{unit}", font=FONT_BODY_BOLD, fg=ACCENT_CYAN, bg=BG_SURFACE)
        lbl_val.pack(side="right")
        tk.Label(card, text=desc, font=FONT_BADGE, fg=TEXT_SECONDARY, bg=BG_SURFACE).pack(anchor="w", pady=(2, 4))
        scale = tk.Scale(card, variable=var, from_=from_, to=to_, orient="horizontal", bg=BG_SURFACE, fg=TEXT_PRIMARY, troughcolor=BG_SUBSURFACE, highlightthickness=0, bd=0, activebackground=ACCENT_CYAN, showvalue=False, cursor="hand2", command=lambda v: lbl_val.config(text=f"{float(v):.1f}{unit}" if is_double else f"{int(float(v))}{unit}"))
        scale.pack(fill="x", pady=(2, 0))
        app_grid.bind_slider_label(var, lbl_val, unit, is_double)
        self._cards.append((card, subtab, f"{title} {desc} {keywords}"))

    def _on_startup_toggle(self) -> None:
        app_grid.handle_startup_toggle(self)

    def sync_mode_buttons(self, mode_val: str) -> None:
        """Synchronize execution mode button highlights without firing on_mode_change."""
        self.var_exec_mode.set(mode_val)
        target_key = "Demo (30s)" if mode_val == "Demo (10s)" and "Demo (30s)" in self._mode_buttons else mode_val
        for val, btn in self._mode_buttons.items():
            active = (val == target_key)
            color = STATUS_RED if val in ("Live", "Demo (30s)") else (STATUS_AMBER if val == "Demo (10s)" else ACCENT_CYAN)
            btn.config(bg="#0D2535" if active else BG_SUBSURFACE, fg=color if active else TEXT_SECONDARY, highlightbackground=color if active else BORDER_MUTED, highlightthickness=1 if active else 0)

    def set_mode(self, mode_val: str) -> None:
        self.sync_mode_buttons(mode_val)
        if self.on_mode_change:
            self.on_mode_change(mode_val)

    def set_subtab(self, subtab_name: str) -> None:
        self.active_subtab = subtab_name.lower()
        for tid, btn in self._subtab_buttons.items():
            act = (tid == self.active_subtab)
            btn.config(bg="#0D2535" if act else BG_SUBSURFACE, fg=ACCENT_CYAN if act else TEXT_SECONDARY, highlightbackground=ACCENT_CYAN if act else BORDER_MUTED)
        self._refresh_cards_visibility()

    def filter_settings(self, query: str) -> None:
        self.search_query = query.strip().lower()
        self._refresh_cards_visibility()

    def _refresh_cards_visibility(self) -> None:
        app_grid.refresh_cards_visibility(self)

    def _on_reset_clicked(self) -> None:
        self.load_config(SettingsConfig())

    def _on_save_clicked(self) -> None:
        cfg = self.get_config()
        self.config = cfg
        self._saved_close_antigravity = bool(self.var_close_antigravity.get())
        self._saved_app_targets = {k: bool(v.get()) for k, v in self.var_app_targets.items()}
        if self.on_save_callback:
            self.on_save_callback(cfg)

    def load_config(self, config: SettingsConfig) -> None:
        """Load clamped SettingsConfig into controls and sync live startup status."""
        self.config = config
        self.config.clamp()
        c = self.config
        self.var_inactivity.set(max(1, c.user_inactivity_sec // 60))
        self.var_timer.set(c.master_shutdown_timer_min)
        self.var_sim_timer.set(getattr(c, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS))
        self.var_cpu.set(getattr(c, "cpu_threshold_pct", 15.0))
        self.var_net.set(getattr(c, "network_threshold_kb", 50.0))
        self.var_audio.set(getattr(c, "audio_inhibit_enabled", True))
        self.var_startup.set(bool(is_startup_enabled()))
        self.var_minimize_tray.set(getattr(c, "minimize_to_tray", True))
        self.var_mini_hud_startup.set(getattr(c, "mini_hud_on_startup", True))
        self.var_target_action.set(getattr(c, "target_action", "Shutdown"))
        self.sync_mode_buttons(getattr(c, "execution_mode", "Live"))
        close_ag = getattr(c, "close_antigravity", True)
        self.var_close_antigravity.set(close_ag)
        targets = getattr(c, "app_closing_targets", {}) or {}
        for app_name, var in self.var_app_targets.items():
            var.set(close_ag if app_name == "AntiGravity" else bool(targets.get(app_name, True)))
        self._saved_close_antigravity = close_ag
        self._saved_app_targets = {k: v.get() for k, v in self.var_app_targets.items()}
        self._update_all_category_states()
        app_grid.update_master_app_counter(self)

    def get_config(self) -> SettingsConfig:
        """Build and clamp SettingsConfig from current UI variable values."""
        close_ag = bool(self.var_close_antigravity.get())
        targets = {k: bool(v.get()) for k, v in self.var_app_targets.items()}
        targets["AntiGravity"] = close_ag
        cfg = SettingsConfig(
            user_inactivity_sec=int(self.var_inactivity.get() * 60), master_shutdown_timer_min=int(self.var_timer.get()), simulation_timer_sec=int(self.var_sim_timer.get()),
            ai_recheck_interval_min=getattr(self.config, "ai_recheck_interval_min", 5), pre_shutdown_close_window_sec=getattr(self.config, "pre_shutdown_close_window_sec", 30),
            waiting_mode=getattr(self.config, "waiting_mode", "Hybrid"), waiting_hybrid_timeout_min=getattr(self.config, "waiting_hybrid_timeout_min", 10),
            cpu_threshold_pct=float(self.var_cpu.get()), network_threshold_kb=float(self.var_net.get()),
            audio_inhibit_enabled=bool(self.var_audio.get()), start_with_windows=bool(self.var_startup.get()),
            minimize_to_tray=bool(self.var_minimize_tray.get()), mini_hud_on_startup=bool(self.var_mini_hud_startup.get()),
            target_action=str(self.var_target_action.get()), execution_mode=str(self.var_exec_mode.get()),
            close_antigravity=close_ag, app_closing_targets=targets,
        )
        cfg.clamp()
        return cfg
