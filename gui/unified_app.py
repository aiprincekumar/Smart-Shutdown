# -*- coding: utf-8 -*-
"""gui.unified_app: Unified Master Desktop Application for Smart Shutdown."""

import logging, tkinter as tk
from typing import Optional, Dict, Any

from core.config import SettingsConfig
from core.coordinator import SentinelCoordinator, LifecycleState
from core.monitor_power import toggle_monitor_power_off
from core.system_tray import create_system_tray_icon, start_tray_icon
from gui.app_event_bridge import (
    GuiLogQueueHandler, apply_mode_change, apply_save_settings, build_merged_context,
    cleanup_app_runtime, dock_app_to_tray, drain_coordinator_events,
    handle_pause_toggle_action, handle_snooze_action, resolve_initial_total_seconds,
    resolve_startup_mode, settings_str_to_mode, sync_ai_snapshot, sync_mini_hud_badges,
    toggle_mini_hud_visibility,
)
from gui.app_event_handlers import (
    handle_mode_change_event, handle_state_change_event, handle_telemetry_data_event,
    handle_tick_event, sync_idle_snap, update_state_display,
)
from gui.components import FloatingMiniOverlay, TitleBarComponent, TargetMode, DashboardView, TelemetryView, LogsView, HistoryView, SettingsView
from gui.components.status_resolver import ResolvedPillState, resolve_sentinel_pill_state, resolve_ai_pill_state, resolve_mode_enum, extract_timer_snapshot
from gui.dialogs import CloseConfirmDialog
from gui.theme import BG_BASE, BORDER_CARD, ACCENT_CYAN, STATUS_GREEN, STATUS_AMBER, STATUS_RED, TEXT_PRIMARY, TEXT_SECONDARY, FONT_BADGE

logger_instance = logging.getLogger("SmartShutdown")


class UnifiedSentinelApp(tk.Tk):
    """Single Unified Master Desktop Application for Smart Shutdown."""

    MODE_LABELS = {
        TargetMode.LIVE: ("⚡ LIVE SHUTDOWN", STATUS_RED), TargetMode.DEMO_30S: ("⚡ DEMO (30s) REAL SHUTDOWN", STATUS_RED),
        TargetMode.SIMULATION: ("🛡️ SIMULATION DRY-RUN", STATUS_AMBER), TargetMode.DEMO_10S: ("🧪 DEMO (10s) SIMULATION", STATUS_AMBER),
    }
    _ARMING_STATES = ("COUNTDOWN_ACTIVE", "PRE_SHUTDOWN_GRACE", "SHUTDOWN_EXECUTED", "AI_EVALUATION", "WAITING_USER_PROMPT")
    _TIMER_KEYS = ("remaining", "idle_sec", "user_inactivity_sec", "idle_threshold", "inactivity_threshold_sec")
    _TV_SYNC_KEYS = ("state", "idle_sec", "idle_threshold", "inactivity_threshold_sec", "audio_active", "has_user_input")

    def __init__(self, coordinator: Optional[SentinelCoordinator] = None, config: Optional[SettingsConfig] = None, dry_run: bool = False, auto_start: bool = True, start_in_mini_hud: bool = False, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.dry_run, self.auto_start, self.start_in_mini_hud = dry_run, auto_start, start_in_mini_hud
        if self.start_in_mini_hud: self.withdraw()
        self.logger = logger or logger_instance
        self.config = config or (coordinator.config if coordinator else SettingsConfig()); self.config.clamp()
        mode0 = resolve_startup_mode(self.config, self.dry_run)
        self.dry_run = mode0 in (TargetMode.SIMULATION, TargetMode.DEMO_10S)
        if self.dry_run and getattr(self.config, "execution_mode", "Live") == "Live": self.config.execution_mode = "Simulation"
        self.coordinator = coordinator or SentinelCoordinator(config=self.config, dry_run=self.dry_run, logger=self.logger)
        self.mini_hud: Optional[FloatingMiniOverlay] = None
        self._event_after_id, self._hud_disarmed, self._last_telemetry_snapshot = None, False, {}
        self.settings_visible, self._is_running, self.is_studio_view, self.current_tab = True, True, True, "dashboard"
        self.total_countdown_seconds = resolve_initial_total_seconds(mode0, self.config)
        self.title("Smart Shutdown"); self.geometry("780x520"); self.minsize(720, 500); self.configure(bg=BG_BASE)
        self._center_window(); self.bind("<Configure>", self._on_configure); self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_window_close_request)
        self.coordinator.attach_event_queue(self.coordinator.event_queue)
        self._log_handler: Optional[GuiLogQueueHandler] = GuiLogQueueHandler(self.coordinator)
        self.logger.addHandler(self._log_handler)
        self.tray_icon = create_system_tray_icon(self)
        if self.tray_icon: start_tray_icon(self.tray_icon)
        self._start_runtime_loops()

    def _start_runtime_loops(self) -> None:
        if self.auto_start:
            self.coordinator.start_background_loop(); self.terminal.append_log("Smart Shutdown coordinator started.", "info")
        if self.start_in_mini_hud:
            self._toggle_mini_hud(); self.terminal.append_log("Started directly in Mini-HUD mode.", "info")
        self._event_after_id = self.after(100, self._process_events)

    def _center_window(self) -> None:
        if not getattr(self, "start_in_mini_hud", False): self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"780x520+{max(0, (sw - 780) // 2)}+{max(0, (sh - 520) // 2 - 20)}")

    def _on_configure(self, event=None) -> None:
        if event and event.widget == self and (event.width >= 600) != self.is_studio_view:
            self.is_studio_view = (event.width >= 600)
            self.dashboard_view.set_studio_view(self.is_studio_view); self.telemetry_view.set_studio_view(self.is_studio_view)

    def _build_ui(self) -> None:
        mode0 = resolve_startup_mode(self.config, self.dry_run)
        self.title_bar = TitleBarComponent(self, on_mode_change=self._on_mode_changed, on_detach_hud=self._toggle_mini_hud, on_tray_minimize=self.dock_to_tray, on_taskbar_minimize=self.iconify, on_close=self._on_window_close_request)
        self.title_bar.pack(fill="x"); self.title_bar.set_mode(mode0)
        m_txt, m_bg = self.MODE_LABELS.get(mode0, ("⚡ LIVE SHUTDOWN", STATUS_RED))
        self.pill_status, self.chip_dryrun = tk.Label(self, text=" IDLE ", bg=STATUS_GREEN), tk.Label(self, text=f" {m_txt} ", bg=m_bg)
        self.btn_hud, self.btn_toggle_cfg = tk.Button(self, text="🪟 Detach Mini HUD", command=self._toggle_mini_hud), tk.Button(self, text="⚙️ Show Settings", command=self._toggle_settings)
        self._build_nav_tabs_bar()
        self.main_container = tk.Frame(self, bg=BG_BASE, padx=8, pady=4, highlightbackground="#06B6D4", highlightthickness=1)
        self.main_container.pack(fill="both", expand=True)
        self._build_dashboard_deck()
        self.telemetry_deck = self.telemetry_view = TelemetryView(self.main_container)
        self.terminal = self.logs_view = LogsView(self.main_container)
        self.history_deck = self.history_view = HistoryView(self.main_container)
        self.settings_deck = self.settings_view = SettingsView(self.main_container, config=self.config, on_save=self._on_save_settings, on_mode_change=self._on_mode_from_settings)
        self.tab_decks = {"dashboard": self.dashboard_view, "telemetry": self.telemetry_view, "logs": self.logs_view, "history": self.history_view, "settings": self.settings_view}
        self.switch_tab("dashboard"); self.settings_visible = True
        st0, rem0 = self._coord_state_name(), self._rem()
        idle_s, idle_t, snap0 = self._sync_idle_snap(st0)
        self.dashboard_view.update_health(snap0)
        self._update_state_display(st0, context=snap0)
        self.update_countdown_display(rem0, max(1, self.total_countdown_seconds), idle_sec=idle_s, idle_threshold=idle_t)

    def _build_nav_tabs_bar(self) -> None:
        self.nav_tabs_bar = tk.Frame(self, bg=BG_BASE, highlightbackground=BORDER_CARD, highlightthickness=1, pady=3, padx=3)
        self.nav_tabs_bar.pack(fill="x", padx=6, pady=(4, 2)); self.nav_tab_buttons: Dict[str, tk.Button] = {}
        for col, (tid, label) in enumerate([("dashboard", "🎛️ Dashboard"), ("telemetry", "📊 Telemetry"), ("logs", "📝 Logs"), ("history", "📜 History"), ("settings", "⚙️ Settings")]):
            self.nav_tabs_bar.grid_columnconfigure(col, weight=1)
            btn = tk.Button(self.nav_tabs_bar, text=label, font=FONT_BADGE, bg="#161B26", fg=TEXT_SECONDARY, activebackground="#1E2638", activeforeground=TEXT_PRIMARY, relief="flat", bd=0, highlightthickness=1, highlightbackground="#1E2838", padx=4, pady=4, cursor="hand2", command=lambda t=tid: self.switch_tab(t))
            btn.grid(row=0, column=col, padx=2, pady=1, sticky="ew")
            btn.bind("<Enter>", lambda _e, b=btn, t=tid: b.config(bg="#1E2638", fg="#E2E8F0", highlightbackground="#2E3F57") if self.current_tab != t else None)
            btn.bind("<Leave>", lambda _e, b=btn, t=tid: b.config(bg="#161B26", fg=TEXT_SECONDARY, highlightbackground="#1E2838") if self.current_tab != t else None)
            self.nav_tab_buttons[tid] = btn

    def switch_tab(self, tab_id: str) -> None:
        if tab_id not in self.tab_decks: return
        self.current_tab = tab_id
        for tid, btn in self.nav_tab_buttons.items():
            act = (tid == tab_id)
            btn.config(bg="#0D2535" if act else "#161B26", fg=ACCENT_CYAN if act else TEXT_SECONDARY, highlightbackground="#06B6D4" if act else "#1E2838", highlightthickness=1)
        for tid, deck in self.tab_decks.items(): deck.pack(fill="both", expand=True) if tid == tab_id else deck.pack_forget()
        self.settings_visible = (tab_id == "settings")
        self.btn_toggle_cfg.config(text="⚙️ Hide Settings" if self.settings_visible else "⚙️ Show Settings")

    def _build_dashboard_deck(self) -> None:
        self.dashboard_view = DashboardView(self.main_container, on_pause=self._on_pause_clicked, on_snooze=lambda: self._on_snooze_clicked(900), on_toggle_monitor=self._on_toggle_monitor_clicked, on_abort=self._on_cancel_clicked, on_bypass_toggle=self._on_bypass_toggle_clicked, on_shutdown_now=self._on_force_shutdown_clicked)
        self.countdown_card = self.dashboard_view
        self.lbl_timer, self.btn_pause, self.btn_snooze, self.btn_cancel, self.canvas_prog = (
            self.dashboard_view.lbl_timer, self.dashboard_view.btn_pause, self.dashboard_view.btn_snooze, self.dashboard_view.btn_abort, self.dashboard_view.canvas_gauge,
        )

    def _coord_state_name(self) -> str:
        st = getattr(self.coordinator, "state", LifecycleState.IDLE_MONITORING)
        return st.value if hasattr(st, "value") else str(st)

    def _rem(self) -> int:
        return getattr(self.coordinator, "remaining_countdown_seconds", self.total_countdown_seconds)

    def _sync_idle_snap(self, st: str, idle_s: Optional[float] = None, **extra: Any) -> tuple: return sync_idle_snap(self, st, idle_s=idle_s, extra=extra)
    def _merged_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: return build_merged_context(self.coordinator, self._last_telemetry_snapshot, extra=extra)

    def _apply_timer_payload(self, data: Dict[str, Any]) -> bool:
        fb_rem = self._last_telemetry_snapshot.get("remaining", getattr(self.coordinator, "remaining_countdown_seconds", 0))
        fb_paused = self._last_telemetry_snapshot.get("is_paused", getattr(self.coordinator, "is_paused", False))
        rem, p, idle_s, thresh_s = extract_timer_snapshot(data, fb_rem, fb_paused)
        if rem > self.total_countdown_seconds: self.total_countdown_seconds = rem
        self.update_countdown_display(rem, self.total_countdown_seconds, is_paused=p, idle_sec=idle_s, idle_threshold=thresh_s)
        return p

    def _process_events(self) -> None:
        if not self._is_running or not self.winfo_exists(): self._event_after_id = None; return
        drain_coordinator_events(self)
        if self._is_running and self.winfo_exists(): self._event_after_id = self.after(100, self._process_events)

    def _handle_mode_change_event(self, data: Dict[str, Any]) -> None: handle_mode_change_event(self, data)
    def _handle_tick_event(self, data: Dict[str, Any]) -> None: handle_tick_event(self, data)
    def _handle_state_change_event(self, data: Dict[str, Any]) -> None: handle_state_change_event(self, data)
    def _handle_telemetry_data_event(self, data: Dict[str, Any]) -> None: handle_telemetry_data_event(self, data)
    def _handle_log_event(self, data: Dict[str, Any]) -> None: self.logs_view.append_log(data.get("message", str(data)), data.get("level", "info"))
    def _handle_ai_state_change_event(self, data: Dict[str, Any]) -> None: self._update_title_bar_ai(data); self.dashboard_view.update_health(data)

    def _update_title_bar_ai(self, data: Optional[Dict[str, Any]] = None) -> None:
        sync_ai_snapshot(self._last_telemetry_snapshot, data)
        ai_key = resolve_ai_pill_state(self._merged_context(), fallback_ai=getattr(self.coordinator, "ai_state", "READY"))
        self.title_bar.set_ai_state(ai_key)
        if self.mini_hud and self.mini_hud.winfo_exists(): self.mini_hud.set_triple_status(ai_state=ai_key)

    def _sync_mini_hud_badges(self, resolved: ResolvedPillState, hud_state: Optional[str] = None, ctx: Optional[Dict[str, Any]] = None) -> None:
        sync_mini_hud_badges(self, resolved, hud_state=hud_state, ctx=ctx)

    def _update_state_display(self, state_name: str, hud_state: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        update_state_display(self, state_name, hud_state=hud_state, context=context)

    def update_countdown_display(self, remaining: int, total: int, is_paused: Optional[bool] = None, idle_sec: Optional[float] = None, idle_threshold: Optional[float] = None) -> None:
        is_p = is_paused if is_paused is not None else getattr(self.coordinator, "is_paused", False)
        if idle_sec is None: idle_sec = self._last_telemetry_snapshot.get("idle_sec", self._last_telemetry_snapshot.get("user_inactivity_sec"))
        if idle_threshold is None: idle_threshold = self._last_telemetry_snapshot.get("idle_threshold", self._last_telemetry_snapshot.get("inactivity_threshold_sec"))
        self.dashboard_view.update_countdown(remaining, total, is_p, idle_sec=idle_sec, idle_threshold=idle_threshold)
        if self.mini_hud and self.mini_hud.winfo_exists(): self.mini_hud.update_countdown(remaining, total, is_p, idle_sec=idle_sec, idle_threshold=idle_threshold)

    def _on_pause_clicked(self) -> None: handle_pause_toggle_action(self)

    def _on_snooze_clicked(self, seconds: int = 300) -> None: handle_snooze_action(self, seconds)

    def _on_toggle_monitor_clicked(self) -> None:
        ok = toggle_monitor_power_off()
        self.terminal.append_log("Displays powered off." if ok else "Failed to toggle monitor power.", "info" if ok else "warn")

    def _on_bypass_toggle_clicked(self) -> None:
        active = self.coordinator.toggle_bypass_inhibitors() if hasattr(self.coordinator, "toggle_bypass_inhibitors") else not getattr(self.coordinator, "bypass_inhibitors", False)
        if not hasattr(self.coordinator, "toggle_bypass_inhibitors"): self.coordinator.bypass_inhibitors = active
        self._last_telemetry_snapshot["bypass_inhibitors"] = active
        self.dashboard_view.set_bypass_state(active); self._update_state_display(self._coord_state_name())
        s = "ACTIVE (Blockers Bypassed)" if active else "OFF (Normal Thresholds)"
        self.terminal.append_log(f"Blocker bypass: {s}.", "warn" if active else "info")
        self.history_view.add_event("blocker", "Blocker Bypass Toggled", "Just now", s)

    def _on_cancel_clicked(self) -> None:
        self.coordinator.cancel_and_reset(); self._hud_disarmed = True
        rem = self._rem(); self.total_countdown_seconds = rem
        idle_s, idle_t, snap = self._sync_idle_snap(LifecycleState.IDLE_MONITORING.value, is_paused=False, remaining=rem, reason="user_cancelled", is_tree_busy=False, worker_count=0, memory_mb=0)
        self._last_telemetry_snapshot.pop("user_inactivity_sec", None)
        self.dashboard_view.update_health(snap); self.telemetry_view.update_telemetry(snap); self._update_state_display(snap["state"], hud_state="DISARMED", context=snap); self.update_countdown_display(rem, rem, is_paused=False, idle_sec=idle_s, idle_threshold=idle_t)
        self.terminal.append_log("Countdown aborted and reset.", "warn")

    def _on_force_shutdown_clicked(self) -> None:
        self.coordinator.force_shutdown_now(); self.terminal.append_log("Force shutdown triggered by user.", "crit")
        self.history_view.add_event("dry_run" if self.dry_run else "power", "⚡ Force Shutdown Triggered", "Just now", "User manual override")

    def _toggle_dry_run(self) -> None:
        self.dry_run = not self.dry_run; self.coordinator.dry_run = self.dry_run
        self._on_mode_changed(TargetMode.SIMULATION if self.dry_run else TargetMode.LIVE)

    def _on_mode_changed(self, new_mode: TargetMode) -> None: apply_mode_change(self, new_mode)
    def _on_mode_from_settings(self, mode_str: str) -> None: self._on_mode_changed(settings_str_to_mode(mode_str))
    def _toggle_settings(self) -> None: self.settings_visible = not self.settings_visible; self.switch_tab("settings" if self.settings_visible else "dashboard")
    def _on_mode_from_mini_hud(self, mode_str: str) -> None: self._on_mode_changed(resolve_mode_enum(mode_str))
    def restore_mini_hud(self) -> None:
        if self.mini_hud and self.mini_hud.winfo_exists():
            ctx = self._merged_context()
            self.mini_hud.restore_hud(idle_sec=ctx.get("idle_sec"), idle_threshold=ctx.get("idle_threshold"))
        else:
            self._toggle_mini_hud()
    def toggle_mini_hud(self) -> None: toggle_mini_hud_visibility(self)
    def _on_dock_mini_hud(self) -> None: self.restore_master_window()
    def dock_to_tray(self) -> None: dock_app_to_tray(self)
    def _on_save_settings(self, new_cfg: SettingsConfig) -> None: apply_save_settings(self, new_cfg)
    def _cleanup_runtime(self) -> None: cleanup_app_runtime(self)

    def restore_master_window(self) -> None:
        self.deiconify(); self.state("normal"); self.lift(); self.focus_force()
        if self.mini_hud and self.mini_hud.winfo_exists():
            try: self.mini_hud.destroy()
            except Exception: pass
            self.mini_hud = None
        self.btn_hud.config(text="🪟 Detach Mini HUD"); self.title_bar.btn_hud.tooltip = "Detach Floating Mini HUD"
        self.terminal.append_log("Master cockpit restored from Mini HUD.", "info")

    def _toggle_mini_hud(self) -> None:
        if self.mini_hud and self.mini_hud.winfo_exists(): self._on_dock_mini_hud(); return
        rem, is_p, ctx = self._rem(), getattr(self.coordinator, "is_paused", False), self._merged_context()
        self.mini_hud = FloatingMiniOverlay(parent=self, on_pause=self._on_pause_clicked, on_resume=self._on_pause_clicked, on_cancel=self._on_cancel_clicked, on_reset=self._on_cancel_clicked, on_dock=self._on_dock_mini_hud, on_tray=self.dock_to_tray, on_mode_toggle=self._on_mode_from_mini_hud, remaining_sec=rem, total_sec=self.total_countdown_seconds)
        self.mini_hud.update_countdown(rem, self.total_countdown_seconds, is_p, idle_sec=ctx.get("idle_sec"), idle_threshold=ctx.get("idle_threshold"))
        sync_mini_hud_badges(self, resolve_sentinel_pill_state(self._coord_state_name(), ctx), ctx=ctx)
        self.btn_hud.config(text="🪟 Dock Mini HUD"); self.title_bar.btn_hud.tooltip = "Dock Floating Mini HUD"
        self.terminal.append_log("Floating Mini-HUD detached.", "info")

    def _on_window_close_request(self) -> None:
        if getattr(self.config, "minimize_to_tray", False) and self.tray_icon is not None: self.dock_to_tray()
        else: CloseConfirmDialog(parent=self, on_minimize=self._minimize_to_background, on_exit=self._shutdown_and_exit)

    def _minimize_to_background(self) -> None:
        self.withdraw(); self.terminal.append_log("Application running in background.", "info")
        if self.mini_hud is None or not self.mini_hud.winfo_exists(): self._toggle_mini_hud()

    def _shutdown_and_exit(self) -> None:
        self._cleanup_runtime()
        try:
            if self.winfo_exists(): self.destroy()
        except Exception: pass

    def destroy(self) -> None:
        self._cleanup_runtime()
        try: super().destroy()
        except tk.TclError: pass


def launch_unified_gui(config: Optional[SettingsConfig] = None, dry_run: bool = False, auto_start: bool = True, start_in_mini_hud: bool = False, logger: Optional[logging.Logger] = None) -> UnifiedSentinelApp:
    app = UnifiedSentinelApp(config=config, dry_run=dry_run, auto_start=auto_start, start_in_mini_hud=start_in_mini_hud, logger=logger)
    app.mainloop(); return app


if __name__ == "__main__":
    launch_unified_gui(dry_run=False)
