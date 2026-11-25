# -*- coding: utf-8 -*-
"""
gui.settings_window: Modern Compact Fluent Dark Settings GUI for Smart Shutdown.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import tkinter as tk
from dataclasses import dataclass, asdict
from typing import Callable, Optional, Dict, Any

# Palette Constants (Fluent Dark)
BG_BASE = "#1E1E24"
BG_SURFACE = "#2B2B36"
ACCENT_COLOR = "#0078D4"
ACCENT_HOVER = "#1084D9"
WARN_COLOR = "#FF8C00"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0A0"
BORDER_COLOR = "#3A3A48"
STATUS_GREEN = "#107C41"
STATUS_YELLOW = "#D8A600"
STATUS_RED = "#D83B01"
FONT_FAMILY = "Segoe UI"

from core.config import SettingsConfig
from core.models import DEFAULT_SIMULATION_SECONDS
from gui.dialogs.close_confirm_dialog import CloseConfirmDialog


class SettingsWindow(tk.Tk):
    """
    Compact modern Fluent Dark settings window (380px x 480px).
    Manages all 5 timing parameters, waiting mode selection, and minimization lifecycle.
    """

    def __init__(
        self,
        config: Optional[SettingsConfig] = None,
        on_save: Optional[Callable[[SettingsConfig], None]] = None,
        on_minimize: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        if config is None or isinstance(config, (tk.Tk, tk.Toplevel)) or not isinstance(config, SettingsConfig):
            self.config = SettingsConfig()
        else:
            self.config = config
        self.config.clamp()
        self.on_save = on_save
        self.on_minimize_callback = on_minimize
        self.on_exit_callback = on_exit

        self.user_inactivity_var = tk.IntVar(value=self.config.user_inactivity_sec)
        self.ai_recheck_var = tk.IntVar(value=self.config.ai_recheck_interval_min)
        self.shutdown_timer_var = tk.IntVar(value=self.config.master_shutdown_timer_min)
        self.app_close_var = tk.IntVar(value=self.config.pre_shutdown_close_window_sec)
        self.waiting_mode_var = tk.StringVar(value=self.config.waiting_mode)

        self._setup_window()
        self._build_header()
        self._build_status_indicator()
        self._build_sliders_container()
        self._build_waiting_mode_section()
        self._build_actions()
        self._bind_lifecycle_events()

    def _setup_window(self) -> None:
        """Configure window geometry, dark theme, and centered position."""
        self.title("Smart Shutdown Settings")
        self.geometry("380x480")
        self.resizable(False, False)
        self.configure(bg=BG_BASE)
        self._center_window(380, 480)

    def _center_window(self, width: int, height: int) -> None:
        """Center the settings window on screen."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_header(self) -> None:
        """Create header with app title and brand styling."""
        hdr = tk.Frame(self, bg=BG_BASE, padx=14, pady=8)
        hdr.pack(fill="x")

        title = tk.Label(
            hdr,
            text="⚡ Smart Shutdown",
            font=(FONT_FAMILY, 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_BASE,
        )
        title.pack(anchor="w")

        sub = tk.Label(
            hdr,
            text="Autonomous Inactivity & Intelligent Power Manager",
            font=(FONT_FAMILY, 8),
            fg=TEXT_SECONDARY,
            bg=BG_BASE,
        )
        sub.pack(anchor="w")

    def _build_status_indicator(self) -> None:
        """Construct the live status badge (AI Working / Idle Polling / Countdown)."""
        card = tk.Frame(self, bg=BG_SURFACE, padx=10, pady=6, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill="x", padx=14, pady=(2, 6))

        self.status_dot = tk.Label(card, text="●", font=(FONT_FAMILY, 11), fg=STATUS_YELLOW, bg=BG_SURFACE)
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_label = tk.Label(
            card,
            text="Idle Polling (Workstation Active)",
            font=(FONT_FAMILY, 8, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
        )
        self.status_label.pack(side="left")

    def _build_sliders_container(self) -> None:
        """Build sliders for all 4 numeric parameters."""
        card = tk.Frame(self, bg=BG_SURFACE, padx=12, pady=6, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill="x", padx=14, pady=4)

        self._create_slider(card, "User Inactivity Threshold", 10, 300, self.user_inactivity_var, "s")
        self._create_slider(card, "AI Re-Check Interval", 1, 30, self.ai_recheck_var, "m")
        self._create_slider(card, "Master Shutdown Timer", 1, 60, self.shutdown_timer_var, "m")
        self._create_slider(card, "Pre-Shutdown App Close Window", 10, 120, self.app_close_var, "s")

    def _create_slider(
        self,
        parent: tk.Frame,
        label: str,
        min_v: int,
        max_v: int,
        var: tk.IntVar,
        unit: str,
    ) -> None:
        """Create a compact slider with label and live value readout."""
        row = tk.Frame(parent, bg=BG_SURFACE)
        row.pack(fill="x", pady=2)

        lbl = tk.Label(row, text=label, font=(FONT_FAMILY, 8), fg=TEXT_PRIMARY, bg=BG_SURFACE)
        lbl.pack(side="left")

        val_lbl = tk.Label(row, text=f"{var.get()}{unit}", font=(FONT_FAMILY, 8, "bold"), fg=WARN_COLOR, bg=BG_SURFACE)
        val_lbl.pack(side="right")

        def _on_move(val: str) -> None:
            val_lbl.config(text=f"{int(float(val))}{unit}")

        scale = tk.Scale(
            parent,
            from_=min_v,
            to=max_v,
            orient="horizontal",
            variable=var,
            showvalue=False,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            troughcolor=BG_BASE,
            activebackground=ACCENT_COLOR,
            highlightthickness=0,
            bd=0,
            command=_on_move,
        )
        scale.pack(fill="x", pady=(0, 4))

    def _build_waiting_mode_section(self) -> None:
        """Construct the tri-modal waiting radio buttons."""
        card = tk.Frame(self, bg=BG_SURFACE, padx=12, pady=6, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill="x", padx=14, pady=4)

        lbl = tk.Label(
            card,
            text="Waiting-on-User Mode (Grill-Me / Prompts)",
            font=(FONT_FAMILY, 8, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
        )
        lbl.pack(anchor="w", pady=(0, 4))

        modes_frame = tk.Frame(card, bg=BG_SURFACE)
        modes_frame.pack(fill="x")

        options = [
            ("Unlimited", "Unlimited"),
            ("Timer", "Timer"),
            ("Hybrid (10m - Default)", "Hybrid"),
        ]

        for text, val in options:
            rb = tk.Radiobutton(
                modes_frame,
                text=text,
                variable=self.waiting_mode_var,
                value=val,
                font=(FONT_FAMILY, 8),
                bg=BG_SURFACE,
                fg=TEXT_PRIMARY,
                selectcolor=BG_BASE,
                activebackground=BG_SURFACE,
                activeforeground=ACCENT_COLOR,
                highlightthickness=0,
                bd=0,
            )
            rb.pack(anchor="w", pady=1)

    def _build_actions(self) -> None:
        """Create Apply and Minimize buttons at the bottom."""
        btn_bar = tk.Frame(self, bg=BG_BASE, padx=14, pady=6)
        btn_bar.pack(fill="x", side="bottom")

        btn_min = tk.Button(
            btn_bar,
            text="🗕 Minimize",
            font=(FONT_FAMILY, 9),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=5,
            command=self.minimize_to_background,
        )
        btn_min.pack(side="left")

        btn_save = tk.Button(
            btn_bar,
            text="💾 Save & Apply",
            font=(FONT_FAMILY, 9, "bold"),
            bg=ACCENT_COLOR,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=14,
            pady=5,
            command=self.save_settings,
        )
        btn_save.pack(side="right")

    def _bind_lifecycle_events(self) -> None:
        """Bind window close protocol and minimize state events."""
        self.protocol("WM_DELETE_WINDOW", self._on_close_requested)

    def _on_close_requested(self) -> None:
        """Prompt dual-choice dialog on window Close (X) click."""
        CloseConfirmDialog(
            parent=self,
            on_minimize=self.minimize_to_background,
            on_exit=self.exit_application,
        )

    def minimize_to_background(self) -> None:
        """Dock silently into background / system tray."""
        self.withdraw()
        if self.on_minimize_callback:
            self.on_minimize_callback()

    def restore_from_background(self) -> None:
        """Restore window from background / system tray."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def exit_application(self) -> None:
        """Completely exit Smart Shutdown application."""
        self.destroy()
        if self.on_exit_callback:
            self.on_exit_callback()

    def get_config(self) -> SettingsConfig:
        """Retrieve current configuration from controls while preserving hidden flags."""
        c = self.config
        cfg = SettingsConfig(
            user_inactivity_sec=self.user_inactivity_var.get(),
            ai_recheck_interval_min=self.ai_recheck_var.get(),
            master_shutdown_timer_min=self.shutdown_timer_var.get(),
            pre_shutdown_close_window_sec=self.app_close_var.get(),
            waiting_mode=self.waiting_mode_var.get(),
            waiting_hybrid_timeout_min=c.waiting_hybrid_timeout_min,
            cpu_threshold_pct=getattr(c, "cpu_threshold_pct", 15.0),
            network_threshold_kb=getattr(c, "network_threshold_kb", 50.0),
            audio_inhibit_enabled=getattr(c, "audio_inhibit_enabled", True),
            start_with_windows=getattr(c, "start_with_windows", False),
            minimize_to_tray=getattr(c, "minimize_to_tray", True),
            mini_hud_on_startup=getattr(c, "mini_hud_on_startup", True),
            target_action=getattr(c, "target_action", "Shutdown"),
            execution_mode=getattr(c, "execution_mode", "Live"),
            simulation_timer_sec=getattr(c, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS),
            close_antigravity=getattr(c, "close_antigravity", True),
            app_closing_targets=dict(getattr(c, "app_closing_targets", {}) or {}),
        )
        cfg.clamp()
        return cfg

    def save_settings(self) -> SettingsConfig:
        """Save settings and invoke callback."""
        cfg = self.get_config()
        self.config = cfg
        if self.on_save:
            self.on_save(cfg)
        return cfg

    def set_status(self, state: str, text: str) -> None:
        """
        Update the live status badge.
        state options: 'working' (green), 'idle' (yellow), 'countdown' (red)
        """
        color_map = {
            "working": STATUS_GREEN,
            "idle": STATUS_YELLOW,
            "countdown": STATUS_RED,
        }
        color = color_map.get(state.lower(), STATUS_YELLOW)
        self.status_dot.config(fg=color)
        self.status_label.config(text=text)


if __name__ == "__main__":
    app = SettingsWindow()
    app.mainloop()
