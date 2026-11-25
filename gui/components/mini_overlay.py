# -*- coding: utf-8 -*-
"""
gui.components.mini_overlay: Ultra-Compact (220x65 px) HWND_TOPMOST Floating Mini-HUD Overlay.
Stays above fullscreen videos/games while remaining 100% synchronized with master window.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Callable, Optional

from core.win32_window import make_hwnd_topmost
from gui.theme import (
    STATUS_GREEN,
    STATUS_AMBER,
    STATUS_RED,
)

# HUD Geometry & Visual Styling Tokens
HUD_WIDTH = 220
HUD_HEIGHT = 65
HUD_BORDER_COLOR = "#06b6d4"  # 1px electric cyan neon border
HUD_BG_DARK = "#0a0e17"       # Matte deep black body
HUD_HEADER_BG = "#111827"     # Dark obsidian header
HUD_DIVIDER = "#1e293b"       # Hairline divider & progress trough
HUD_BTN_BG = "#1e293b"        # Slate button surface
HUD_BTN_FG = "#f1f5f9"        # White icon
HUD_BTN_ACTIVE_BG = "#334155" # Active hover

# Compact Typography Tokens
FONT_HUD_BRAND = ("Segoe UI", 8, "bold")
FONT_HUD_BADGE = ("Segoe UI", 7, "bold")
FONT_HUD_TIMER = ("Consolas", 16, "bold")
FONT_HUD_INACTIVITY = ("Consolas", 9, "bold")
FONT_HUD_BTN = ("Segoe UI", 8, "normal")


class FloatingMiniOverlay(tk.Toplevel):
    """
    Ultra-Compact Topmost Floating HUD (220px x 65px) positioned at top-right of screen.
    Features 20px Triple-Status Header Bar, 40px Action Row with 4-Button Cluster,
    and 3px bottom micro-progress bar with Context7 event shielding.
    """

    def __init__(
        self,
        parent: tk.Tk,
        on_pause: Optional[Callable[[], None]] = None,
        on_resume: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        on_dock: Optional[Callable[[], None]] = None,
        on_tray: Optional[Callable[[], None]] = None,
        on_mode_toggle: Optional[Callable[[str], None]] = None,
        remaining_sec: Optional[int] = None,
        total_sec: Optional[int] = None,
        idle_sec: Optional[float] = None,
        idle_threshold: Optional[float] = None,
        **kwargs
    ):
        super().__init__(parent, bg=HUD_BG_DARK, **kwargs)
        self._init_hud_state(
            parent, on_pause, on_resume, on_cancel, on_reset,
            on_dock, on_tray, on_mode_toggle, remaining_sec, total_sec,
        )
        self._configure_hud_window()
        self._position_top_right()
        self._build_ui()
        self._bind_mouse_drag()
        self._enforce_topmost()
        if idle_threshold is not None:
            self._last_idle_threshold = idle_threshold
        if idle_sec is not None:
            self.update_countdown(
                self.remaining_sec, self.total_sec, self.is_paused,
                idle_sec=idle_sec, idle_threshold=idle_threshold,
            )

    def _init_hud_state(
        self, parent: tk.Tk, on_pause, on_resume, on_cancel, on_reset,
        on_dock, on_tray, on_mode_toggle, remaining_sec: Optional[int], total_sec: Optional[int],
    ) -> None:
        """Initialize callbacks, timer counters, mode list, and drag state."""
        self.master_app = parent
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_reset = on_reset or on_cancel
        self.on_cancel = on_cancel or self.on_reset
        self.on_dock = on_dock
        self.on_tray = on_tray
        self.on_mode_toggle = on_mode_toggle
        self.remaining_sec = max(0, remaining_sec) if remaining_sec is not None else 900
        self.total_sec = max(1, total_sec) if total_sec is not None else 900
        self.is_paused = False
        self._last_idle_sec: Optional[float] = None
        self._last_idle_threshold: Optional[float] = None
        self._current_mode_idx = 0
        self._modes = [
            ("⚡ Live", "#1e1b4b", "#818cf8"),
            ("🧪 Demo", "#064e3b", "#34d399"),
            ("🛡️ Sim", "#701a75", "#f472b6"),
        ]
        self._drag_data = {"x": 0, "y": 0}

    def _configure_hud_window(self) -> None:
        """Configure frameless topmost window geometry and border."""
        self.title("Smart Shutdown HUD")
        self.geometry(f"{HUD_WIDTH}x{HUD_HEIGHT}")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(highlightbackground=HUD_BORDER_COLOR, highlightthickness=1)

    def _enforce_topmost(self) -> None:
        """Enforce HWND_TOPMOST for fullscreen coverage."""
        try:
            hwnd = int(self.wm_frame(), 16) if hasattr(self, "wm_frame") else self.winfo_id()
            make_hwnd_topmost(hwnd)
        except Exception:
            pass

    def _position_top_right(self) -> None:
        """Position overlay at top-right corner with 16px horizontal and 24px vertical margin."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        x = max(0, sw - HUD_WIDTH - 16)
        y = 24
        self.geometry(f"{HUD_WIDTH}x{HUD_HEIGHT}+{x}+{y}")

    def _build_ui(self) -> None:
        """Construct the ultra-compact HUD layout (220x65 px)."""
        self.container = tk.Frame(self, bg=HUD_BG_DARK, width=HUD_WIDTH, height=HUD_HEIGHT)
        self.container.pack_propagate(False)
        self.container.pack(fill="both", expand=True)

        self._build_triple_status_header(self.container)
        self._build_body_and_cluster(self.container)
        self._build_micro_progress(self.container)

    def _build_triple_status_header(self, parent_frame: tk.Frame) -> None:
        """Construct 20px header bar with branding and 3 micro status badges."""
        self.bar = tk.Frame(parent_frame, bg=HUD_HEADER_BG, height=20, cursor="fleur", padx=4, pady=0)
        self.bar.pack(fill="x", side="top")
        self.bar.pack_propagate(False)

        # Left branding
        self.lbl_drag = tk.Label(
            self.bar, text="⚡ HUD", bg=HUD_HEADER_BG, fg="#f8fafc",
            font=FONT_HUD_BRAND, cursor="fleur"
        )
        self.lbl_drag.pack(side="left", padx=(2, 4))

        # Right triple-status badge cluster
        self.badges_box = tk.Frame(self.bar, bg=HUD_HEADER_BG)
        self.badges_box.pack(side="right", padx=(0, 2))

        # 1. AI Work State badge
        self.badge_ai = tk.Label(
            self.badges_box, text="✨ Ready", bg="#064e3b", fg="#34d399",
            font=FONT_HUD_BADGE, padx=3, pady=0
        )
        self.badge_ai.pack(side="left", padx=1)

        # 2. Sentinel/Timer State badge (Aliased as pill_state for compatibility)
        self.badge_sentinel = tk.Label(
            self.badges_box, text="💤 Idle", bg="#1e293b", fg="#94a3b8",
            font=FONT_HUD_BADGE, padx=3, pady=0
        )
        self.badge_sentinel.pack(side="left", padx=1)
        self.pill_state = self.badge_sentinel

        # 3. Target Mode Switcher (Clickable)
        self.badge_mode = tk.Label(
            self.badges_box, text="⚡ Live", bg="#1e1b4b", fg="#818cf8",
            font=FONT_HUD_BADGE, padx=3, pady=0, cursor="hand2"
        )
        self.badge_mode.pack(side="left", padx=1)
        self.badge_mode.bind("<Button-1>", self._on_toggle_mode)

        # 1px hairline divider
        divider = tk.Frame(parent_frame, bg=HUD_DIVIDER, height=1)
        divider.pack(fill="x", side="top")

    def _build_body_and_cluster(self, parent_frame: tk.Frame) -> None:
        """Construct the 40px main action row with digital countdown and 4-button cluster."""
        self.body = tk.Frame(parent_frame, bg=HUD_BG_DARK, height=41, padx=4, pady=2)
        self.body.pack(fill="x", side="top")
        self.body.pack_propagate(False)

        self.mid_row = tk.Frame(self.body, bg=HUD_BG_DARK)
        self.mid_row.pack(fill="both", expand=True)

        # Digital Countdown Clock
        m = self.remaining_sec // 60
        s = self.remaining_sec % 60
        self.lbl_timer = tk.Label(
            self.mid_row, text=f"{m:02d}:{s:02d}", bg=HUD_BG_DARK, fg="#00f2fe",
            font=FONT_HUD_TIMER, cursor="fleur"
        )
        self.lbl_timer.pack(side="left", padx=(2, 4))

        # Secondary Physical User Inactivity Chip
        self.chip_inactivity = tk.Label(
            self.mid_row, text="0:00", bg="#1e1b4b", fg="#c084fc",
            font=FONT_HUD_INACTIVITY, padx=3, pady=0, cursor="fleur"
        )
        self.chip_inactivity.pack(side="left", padx=(0, 4))

        # 4-Action Button Cluster
        self._build_action_button_cluster(self.mid_row)

    def _build_action_button_cluster(self, parent_frame: tk.Frame) -> None:
        """Construct 4-action button cluster (Pause, Reset, Tray, Expand/Dock)."""
        self.btn_box = tk.Frame(parent_frame, bg=HUD_BG_DARK)
        self.btn_box.pack(side="right", padx=(0, 2))

        # 1. Pause / Resume Toggle
        self.btn_pause = tk.Button(
            self.btn_box, text="⏸", bg=HUD_BTN_BG, fg=HUD_BTN_FG,
            activebackground=HUD_BTN_ACTIVE_BG, activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT_HUD_BTN, padx=4, pady=1,
            command=self._toggle_pause, cursor="hand2"
        )
        self.btn_pause.pack(side="left", padx=1)

        # 2. Reset Button (In-place) - Aliased as btn_cancel
        self.btn_reset = tk.Button(
            self.btn_box, text="🔄", bg=HUD_BTN_BG, fg=HUD_BTN_FG,
            activebackground=HUD_BTN_ACTIVE_BG, activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT_HUD_BTN, padx=4, pady=1,
            command=self._trigger_reset, cursor="hand2"
        )
        self.btn_reset.pack(side="left", padx=1)
        self.btn_cancel = self.btn_reset

        # 3. Minimize to Tray Button
        self.btn_tray = tk.Button(
            self.btn_box, text="📥", bg=HUD_BTN_BG, fg=HUD_BTN_FG,
            activebackground=HUD_BTN_ACTIVE_BG, activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT_HUD_BTN, padx=4, pady=1,
            command=self._trigger_tray, cursor="hand2"
        )
        self.btn_tray.pack(side="left", padx=1)

        # 4. Expand to Normal Cockpit - Aliased as btn_dock
        self.btn_expand = tk.Button(
            self.btn_box, text="🪟", bg=HUD_BTN_BG, fg=HUD_BTN_FG,
            activebackground=HUD_BTN_ACTIVE_BG, activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT_HUD_BTN, padx=4, pady=1,
            command=self._on_expand_to_main, cursor="hand2"
        )
        self.btn_expand.pack(side="left", padx=1)
        self.btn_dock = self.btn_expand

    def _build_micro_progress(self, parent_frame: tk.Frame) -> None:
        """Construct 4px dual-tier micro-progress bar canvas at bottom edge."""
        self.canvas_prog = tk.Canvas(
            parent_frame, bg=HUD_DIVIDER, height=4, highlightthickness=0, bd=0
        )
        self.canvas_prog.pack(fill="x", side="bottom")

    def _bind_mouse_drag(self) -> None:
        """Allow dragging designated areas and double-clicking to expand to master cockpit."""
        interactive_widgets = (self.bar, self.lbl_drag, self.body, self.lbl_timer, self.pill_state, self.chip_inactivity)
        for widget in interactive_widgets:
            widget.bind("<ButtonPress-1>", self._on_start_drag)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<Double-Button-1>", self._on_expand_to_main)

        # Context7 Event Shielding: Shield button container and buttons against mouse event bubbling
        for evt in ("<Double-Button-1>", "<ButtonPress-1>", "<B1-Motion>"):
            self.btn_box.bind(evt, lambda e: "break")

        for btn in (self.btn_pause, self.btn_reset, self.btn_tray, self.btn_expand):
            btn.bind("<Double-Button-1>", lambda e: "break")
            btn.bind("<B1-Motion>", lambda e: "break")
            btn.bind("<ButtonPress-1>", self._on_button_press_shield)

    def _on_button_press_shield(self, event) -> Optional[str]:
        """Shield buttons from window drag while preserving standard button click activation."""
        self._drag_data["x"] = self._drag_data["y"] = 0
        return None

    def _on_start_drag(self, event) -> None:
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event) -> None:
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def _toggle_pause(self) -> None:
        """Toggle pause/resume state in-place without restoring master window."""
        if not self.is_paused:
            self.is_paused = True
            self.btn_pause.config(text="▶")
            self.set_triple_status(sentinel_state="Paused")
            if self.on_pause:
                self.on_pause()
        else:
            self.is_paused = False
            self.btn_pause.config(text="⏸")
            if self.on_resume:
                self.on_resume()
            else:
                self.set_triple_status(sentinel_state="Running")

    def _trigger_reset(self) -> None:
        """Reset countdown timer back to configured duration in-place."""
        self.is_paused = False
        self.btn_pause.config(text="⏸")
        self.set_state("DISARMED", STATUS_GREEN)
        if self.on_reset:
            self.on_reset()
        elif self.on_cancel:
            self.on_cancel()

    def _trigger_cancel(self) -> None: self._trigger_reset()
    def _trigger_dock(self) -> None: self._on_expand_to_main()

    def _trigger_tray(self) -> None:
        """Minimize HUD overlay into Windows System Tray."""
        if self.on_tray:
            self.on_tray()
        elif hasattr(self.master_app, "dock_to_tray"):
            self.master_app.dock_to_tray()
        else:
            self.withdraw()
            if hasattr(self.master_app, "terminal"):
                self.master_app.terminal.append_log("Smart Shutdown HUD docked in system tray.", "info")

    def restore_hud(
        self,
        idle_sec: Optional[float] = None,
        idle_threshold: Optional[float] = None,
    ) -> None:
        """Restore HUD from system tray or hidden state back to topmost position."""
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self._enforce_topmost()
        if idle_sec is not None:
            self.update_countdown(
                self.remaining_sec, self.total_sec, self.is_paused,
                idle_sec=idle_sec, idle_threshold=idle_threshold,
            )

    def _on_expand_to_main(self, event=None) -> None:
        """Restores master cockpit window and docks/closes the mini overlay."""
        if hasattr(self.master_app, "restore_master_window"):
            self.master_app.restore_master_window()
            return
        if self.on_dock:
            self.on_dock()
            return
        if not self.winfo_exists():
            return
        try:
            self.destroy()
        except Exception:
            pass

    def _on_toggle_mode(self, event=None) -> None:
        """Cycle target mode between Live, Demo, and Sim."""
        self._current_mode_idx = (self._current_mode_idx + 1) % len(self._modes)
        label_text, bg_col, fg_col = self._modes[self._current_mode_idx]
        self.badge_mode.config(text=label_text, bg=bg_col, fg=fg_col)
        if self.on_mode_toggle:
            self.on_mode_toggle(label_text)

    def _update_ai_badge(self, ai_state: Optional[str]) -> None:
        raw = "" if ai_state is None else str(ai_state)
        al = raw.strip().lower()
        if "work" in al or "busy" in al: self.badge_ai.config(text="⚙️ Working", bg="#083344", fg="#38bdf8")
        elif "wait" in al or "input" in al: self.badge_ai.config(text="💬 Waiting", bg="#4c1d95", fg="#c084fc")
        elif "ready" in al or "idle" in al or not al: self.badge_ai.config(text="✨ Ready", bg="#064e3b", fg="#34d399")
        else: self.badge_ai.config(text=f" {raw.strip()} ", bg="#083344", fg="#38bdf8")

    def _update_sentinel_badge(self, sentinel_state: Optional[str]) -> None:
        raw = "" if sentinel_state is None else str(sentinel_state)
        st_lower = raw.strip().lower()
        mapping = [
            (("disarm",), (" DISARMED ", STATUS_GREEN, "#ffffff")),
            (("clos", "grace"), ("🚪 Closing", "#78350f", "#fcd34d")),
            (("shut", "crit"), ("⚡ Shutdown", "#7f1d1d", "#fca5a5")),
            (("paus",), ("⏸️ Paused", "#78350f", "#fcd34d")),
            (("block",), ("🛑 Blocked", "#7f1d1d", "#fca5a5")),
            (("waiting_user", "prompt", "waiting"), ("💬 Waiting", "#4c1d95", "#c084fc")),
            (("ai_eval", "eval"), ("🔍 Eval", "#083344", "#38bdf8")),
            (("run", "count", "⏱"), ("⏱️ Running", "#064e3b", "#34d399")),
            (("away", "👤"), ("👤 Away", "#064e3b", "#34d399")),
            (("active",), ("🟢 Active", "#064e3b", "#34d399")),
            (("idle", "idle_monitoring", "aborted_reset", "abort"), ("💤 Idle", "#1e293b", "#94a3b8")),
        ]
        for keys, (txt, bg, fg) in mapping:
            if any(k in st_lower for k in keys):
                self.badge_sentinel.config(text=txt, bg=bg, fg=fg)
                return
        self.badge_sentinel.config(text=f" {raw.strip()} ")

    def _update_mode_badge(self, mode: Optional[str]) -> None:
        raw = "" if mode is None else str(mode)
        m_lower = raw.strip().lower()
        if "live" in m_lower: self._current_mode_idx = 0; self.badge_mode.config(text="⚡ Live", bg="#1e1b4b", fg="#818cf8")
        elif "demo" in m_lower: self._current_mode_idx = 1; self.badge_mode.config(text="🧪 Demo", bg="#064e3b", fg="#34d399")
        elif "sim" in m_lower or "dry" in m_lower: self._current_mode_idx = 2; self.badge_mode.config(text="🛡️ Sim", bg="#701a75", fg="#f472b6")
        else: self.badge_mode.config(text=f" {raw.strip()} ")

    def set_triple_status(
        self,
        ai_state: Optional[str] = None,
        sentinel_state: Optional[str] = None,
        mode: Optional[str] = None,
        mode_state: Optional[str] = None,
    ) -> None:
        """Update all three micro-status badges in the header."""
        mode = mode or mode_state
        if ai_state is not None:
            self._update_ai_badge(ai_state)
        if sentinel_state is not None:
            self._update_sentinel_badge(sentinel_state)
        if mode is not None:
            self._update_mode_badge(mode)

    def set_state(self, state_text: str, color: str) -> None:
        """Update sentinel state badge (preserves backward compatibility)."""
        clean_text = state_text.strip()
        self.badge_sentinel.config(text=f" {clean_text} ", bg=color, fg="#ffffff")

    def update_countdown(
        self,
        remaining_sec: int,
        total_sec: int,
        is_paused: bool = False,
        idle_sec: Optional[float] = None,
        idle_threshold: Optional[float] = None,
    ) -> None:
        """Update digital timer label, inactivity chip, pause state, and 4px dual micro-progress bar."""
        self.remaining_sec = max(0, remaining_sec)
        self.total_sec = max(1, total_sec)
        self.is_paused = is_paused
        self.btn_pause.config(text="▶" if is_paused else "⏸")
        if idle_sec is None:
            idle_sec = self._last_idle_sec
        else:
            self._last_idle_sec = idle_sec
        if idle_threshold is None:
            idle_threshold = self._last_idle_threshold
        else:
            self._last_idle_threshold = idle_threshold

        m, s = self.remaining_sec // 60, self.remaining_sec % 60
        self.lbl_timer.config(text=f"{m:02d}:{s:02d}")
        if idle_sec is not None and idle_sec > 0:
            im, isec = int(idle_sec) // 60, int(idle_sec) % 60
            self.chip_inactivity.config(text=f"{im}:{isec:02d}")
        else:
            self.chip_inactivity.config(text="0:00")
        self._draw_micro_progress(idle_sec, idle_threshold)

    def _draw_micro_progress(
        self, idle_sec: Optional[float], idle_threshold: Optional[float]
    ) -> None:
        """Draw 4px dual-tier micro-progress bar across countdown and inactivity slices."""
        self.canvas_prog.delete("all")
        w = self.canvas_prog.winfo_width()
        if w <= 1:
            w = HUD_WIDTH

        pct = max(0.0, min(1.0, self.remaining_sec / self.total_sec))
        fill_w = int(w * pct)
        if self.remaining_sec > 60:
            top_color = "#06b6d4"
        elif self.remaining_sec > 30:
            top_color = "#f59e0b"
        else:
            top_color = "#ef4444"
        if fill_w > 0:
            self.canvas_prog.create_rectangle(0, 0, fill_w, 2, fill=top_color, outline="")

        thresh = float(idle_threshold) if idle_threshold and idle_threshold > 0 else 60.0
        idle_ratio = max(0.0, min(1.0, float(idle_sec or 0.0) / thresh))
        idle_w = int(w * idle_ratio)
        bottom_color = "#f59e0b" if idle_ratio > 0.85 else ("#8b5cf6" if idle_ratio >= 0.50 else "#10b981")
        if idle_w > 0:
            self.canvas_prog.create_rectangle(0, 2, idle_w, 4, fill=bottom_color, outline="")
