# -*- coding: utf-8 -*-
"""
gui.components.settings_deck: Collapsible / Embedded Settings Panel.
Provides sliders for timing parameters, waiting mode selection, presets, and save actions.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Callable, Optional

from core.models import DEFAULT_SIMULATION_SECONDS
from gui.settings_window import SettingsConfig
from gui.theme import (
    BG_SURFACE,
    BG_SUBSURFACE,
    BORDER_COLOR,
    ACCENT_BLUE,
    ACCENT_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    FONT_SUBHEADER,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class SettingsDeck(tk.Frame):
    """Embedded settings panel with 5 sliders, waiting mode, presets, and save action."""

    def __init__(
        self,
        parent: tk.Widget,
        config: Optional[SettingsConfig] = None,
        on_save: Optional[Callable[[SettingsConfig], None]] = None,
        **kwargs
    ):
        super().__init__(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=12, pady=10, **kwargs)
        self.config = config or SettingsConfig()
        self.config.clamp()
        self.on_save_callback = on_save

        self._build_ui()
        self.load_config(self.config)

    def _build_ui(self) -> None:
        """Construct the settings sliders, radio buttons, and action buttons."""
        tk.Label(
            self,
            text="⚙️ Smart Shutdown Timers & Automation Governance",
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            font=FONT_SUBHEADER,
        ).pack(anchor="w", pady=(0, 8))
        self._build_sliders_grid()
        self._build_action_row()

    def _build_sliders_grid(self) -> None:
        """Construct the 5 timing sliders and waiting policy radio selector."""
        grid_frame = tk.Frame(self, bg=BG_SURFACE)
        grid_frame.pack(fill="x", expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        slider_specs = (
            ("var_inactivity", "lbl_inactivity", "user_inactivity_sec", 0, 0, "User Inactivity (10-300s):", 10, 300, "s"),
            ("var_recheck", "lbl_recheck", "ai_recheck_interval_min", 0, 1, "AI Recheck Interval (1-30m):", 1, 30, "m"),
            ("var_timer", "lbl_timer", "master_shutdown_timer_min", 1, 0, "Master Shutdown Timer (1-60m):", 1, 60, "m"),
            ("var_close_win", "lbl_close_win", "pre_shutdown_close_window_sec", 1, 1, "Pre-Shutdown Close Window (10-120s):", 10, 120, "s"),
            ("var_hybrid", "lbl_hybrid", "waiting_hybrid_timeout_min", 2, 0, "Hybrid Prompt Timeout (1-60m):", 1, 60, "m"),
        )
        for var_attr, lbl_attr, cfg_attr, row, col, label, lo, hi, unit in slider_specs:
            var = tk.IntVar(value=getattr(self.config, cfg_attr))
            setattr(self, var_attr, var)
            setattr(self, lbl_attr, self._create_slider_row(grid_frame, row=row, col=col, label=label, var=var, from_=lo, to=hi, unit=unit))
        self._build_waiting_mode_radios(grid_frame)

    def _build_waiting_mode_radios(self, grid_frame: tk.Frame) -> None:
        """Construct the Waiting Gate Policy radio button selector."""
        self.var_mode = tk.StringVar(value=self.config.waiting_mode)
        mode_frame = tk.Frame(grid_frame, bg=BG_SURFACE)
        mode_frame.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        tk.Label(mode_frame, text="Waiting Gate Policy:", bg=BG_SURFACE, fg=TEXT_SECONDARY, font=FONT_BODY).pack(anchor="w")
        r_box = tk.Frame(mode_frame, bg=BG_SURFACE)
        r_box.pack(anchor="w", pady=(2, 0))
        for mode in ("Hybrid", "Fixed Timer", "Unlimited"):
            tk.Radiobutton(
                r_box, text=mode, variable=self.var_mode, value=mode,
                bg=BG_SURFACE, fg=TEXT_PRIMARY, selectcolor=BG_SUBSURFACE,
                activebackground=BG_SURFACE, activeforeground=TEXT_PRIMARY, font=FONT_BODY,
            ).pack(side="left", padx=3)

    def _build_action_row(self) -> None:
        """Construct quick preset buttons and Save/Reset action buttons."""
        action_row = tk.Frame(self, bg=BG_SURFACE)
        action_row.pack(fill="x", pady=(10, 0))
        tk.Label(action_row, text="Presets:", bg=BG_SURFACE, fg=TEXT_SECONDARY, font=FONT_BODY).pack(side="left", padx=(0, 4))
        for text, preset in (
            ("30s Test", (10, 1, 1, 10, 1, "Hybrid")),
            ("5m Std", (60, 5, 5, 30, 5, "Hybrid")),
            ("15m Prod", (60, 5, 15, 30, 10, "Hybrid")),
        ):
            tk.Button(
                action_row, text=text, bg=BG_SUBSURFACE, fg=TEXT_PRIMARY,
                activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
                relief="flat", font=FONT_BODY, padx=6, pady=2,
                command=lambda p=preset: self._apply_preset(*p),
            ).pack(side="left", padx=2)
        self.btn_save = tk.Button(
            action_row, text="💾 Save Settings", bg=ACCENT_BLUE, fg=TEXT_PRIMARY,
            activebackground=ACCENT_HOVER, activeforeground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY_BOLD, padx=10, pady=2, command=self._on_save_clicked,
        )
        self.btn_save.pack(side="right", padx=(4, 0))
        tk.Button(
            action_row, text="↺ Reset", bg=BG_SUBSURFACE, fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY, padx=8, pady=2, command=self._on_reset_clicked,
        ).pack(side="right", padx=2)

    def _create_slider_row(self, parent: tk.Widget, row: int, col: int, label: str, var: tk.IntVar, from_: int, to: int, unit: str):
        """Build an interactive slider with numeric display."""
        frame = tk.Frame(parent, bg=BG_SURFACE)
        frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=4)

        header = tk.Frame(frame, bg=BG_SURFACE)
        header.pack(fill="x")
        tk.Label(header, text=label, bg=BG_SURFACE, fg=TEXT_SECONDARY, font=FONT_BODY).pack(side="left")
        lbl_val = tk.Label(header, text=f"{var.get()}{unit}", bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_BODY_BOLD)
        lbl_val.pack(side="right")

        def _on_change(val_str):
            lbl_val.config(text=f"{int(float(val_str))}{unit}")

        scale = tk.Scale(
            frame, from_=from_, to=to, orient="horizontal", variable=var,
            showvalue=False, command=_on_change, bg=BG_SURFACE, fg=TEXT_PRIMARY,
            troughcolor=BG_SUBSURFACE, activebackground=ACCENT_HOVER,
            highlightthickness=0, bd=0
        )
        scale.pack(fill="x", pady=(2, 0))
        return lbl_val

    def _apply_preset(self, inact: int, rchk: int, tmr: int, cls_win: int, hyb: int, mode: str) -> None:
        """Apply predefined timing preset values."""
        self.var_inactivity.set(inact)
        self.lbl_inactivity.config(text=f"{inact}s")
        self.var_recheck.set(rchk)
        self.lbl_recheck.config(text=f"{rchk}m")
        self.var_timer.set(tmr)
        self.lbl_timer.config(text=f"{tmr}m")
        self.var_close_win.set(cls_win)
        self.lbl_close_win.config(text=f"{cls_win}s")
        self.var_hybrid.set(hyb)
        self.lbl_hybrid.config(text=f"{hyb}m")
        self.var_mode.set(mode)

    def _on_reset_clicked(self) -> None:
        """Restore factory defaults."""
        default_cfg = SettingsConfig()
        self.load_config(default_cfg)

    def _on_save_clicked(self) -> None:
        """Harvest inputs and fire save callback."""
        cfg = self.get_config()
        if self.on_save_callback:
            self.on_save_callback(cfg)

    def load_config(self, cfg: SettingsConfig) -> None:
        """Synchronize inputs with an existing SettingsConfig instance."""
        self.config = cfg
        self.config.clamp()
        self._apply_preset(
            cfg.user_inactivity_sec,
            cfg.ai_recheck_interval_min,
            cfg.master_shutdown_timer_min,
            cfg.pre_shutdown_close_window_sec,
            cfg.waiting_hybrid_timeout_min,
            cfg.waiting_mode
        )

    def get_config(self) -> SettingsConfig:
        """Construct a validated SettingsConfig from UI values while preserving hidden flags."""
        c = self.config
        cfg = SettingsConfig(
            user_inactivity_sec=self.var_inactivity.get(),
            ai_recheck_interval_min=self.var_recheck.get(),
            master_shutdown_timer_min=self.var_timer.get(),
            pre_shutdown_close_window_sec=self.var_close_win.get(),
            waiting_mode=self.var_mode.get(),
            waiting_hybrid_timeout_min=self.var_hybrid.get(),
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
