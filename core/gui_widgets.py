# -*- coding: utf-8 -*-
"""
core.gui_widgets: Modular UI widget construction and styling helpers for CountdownWindow.
Universal Rule 28 Architectural Modularity Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Tuple, Callable

PALETTE = {
    "bg_dark": "#181825", "card_bg": "#1e1e2e", "card_border": "#313244",
    "text_white": "#cdd6f4", "text_dim": "#a6adc8", "accent_blue": "#89b4fa",
    "accent_amber": "#f9e2af", "accent_red": "#f38ba8", "accent_green": "#a6e3a1",
    "accent_cyan": "#89dceb", "btn_dark_fg": "#11111b",
}

BANNER_COMPLETE_EN = "Antigravity Tasks Completed! Timer is running.\nYou want to cancel or continue?"
BANNER_COMPLETE_HI = "सभी Antigravity कार्य पूर्ण हो चुके हैं! टाइमर चालू है।\nक्या आप शटडाउन रद्द करना चाहते हैं या तुरंत जारी रखना चाहते हैं?"
BANNER_ACTIVE_EN = "Antigravity Task in Progress! Timer is auto-paused.\nYou can cancel, wait for completion, or shutdown now."
BANNER_ACTIVE_HI = "Antigravity कार्य प्रगति पर है! टाइमर ऑटो-पॉज़ है।\nकार्य पूरा होने पर टाइमर अपने आप चालू हो जाएगा।"

BTN_PAUSE_STYLES = {
    "pause": {"text": "⏸️ Pause", "bg": "#45475a", "fg": "#cdd6f4", "activebackground": "#585b70", "activeforeground": "#ffffff"},
    "resume": {"text": "▶️ Resume", "bg": "#a6e3a1", "fg": "#11111b", "activebackground": "#86d381", "activeforeground": "#11111b"},
    "auto_paused": {"text": "⏸️ Auto-Paused", "bg": "#f9e2af", "fg": "#11111b", "activebackground": "#f5a97f", "activeforeground": "#11111b"},
}


def format_countdown_time(seconds: int) -> str:
    """Format remaining seconds as MM:SS."""
    clamped = max(0, int(seconds))
    return f"{clamped // 60:02d}:{clamped % 60:02d}"


def truncate_text(text: str, limit: int = 80) -> str:
    """Truncate text to fit cleanly within UI labels."""
    return text if len(text) <= limit else text[: limit - 3] + "..."


def resolve_mode_badge(dry_run: bool, skip_shutdown: bool) -> Tuple[str, str]:
    """Return status badge text and foreground color for the active execution mode."""
    if dry_run:
        return "⚠️ SAFE TEST / DRY RUN MODE · PC WILL NOT POWER OFF", PALETTE["accent_amber"]
    if skip_shutdown:
        return "⚠️ TEST MODE · REAL APP CLOSURE AT T-10s (SHUTDOWN SKIPPED)", PALETTE["accent_amber"]
    return "🟢 ALL ANTIGRAVITY TASKS CERTIFIED COMPLETE", PALETTE["accent_green"]


def resolve_auto_pause_badge(blocking_reason: str) -> str:
    """Resolve badge label for an active Antigravity blocker."""
    lower = blocking_reason.lower()
    if "awaiting silence buffer" in lower:
        return "⏸️ AUTO-PAUSED · SETTLING BUFFER"
    if "waiting for user" in lower:
        return "⏸️ AUTO-PAUSED · WAITING FOR USER INPUT"
    return "⏸️ AUTO-PAUSED · COMMAND/TASK IN PROGRESS"


def apply_pause_button_style(btn: tk.Button, style_key: str) -> None:
    """Apply a predefined pause/resume/auto-paused style to the pause button."""
    btn.configure(**BTN_PAUSE_STYLES[style_key])


def set_banner_text(win, active_task: bool) -> None:
    """Update bilingual banner labels to match task completion vs active progress."""
    if not (hasattr(win, "lbl_banner_en") and hasattr(win, "lbl_banner_hi")):
        return
    win.lbl_banner_en.configure(text=BANNER_ACTIVE_EN if active_task else BANNER_COMPLETE_EN)
    win.lbl_banner_hi.configure(text=BANNER_ACTIVE_HI if active_task else BANNER_COMPLETE_HI)


def _create_action_button(
    parent: tk.Frame, text: str, bg: str, fg: str, active_bg: str, active_fg: str,
    command: Callable[[], None], bold: bool = True, pack_padx: object = 3,
) -> tk.Button:
    """Create and pack a flat themed action button inside the bottom bar."""
    font = ("Segoe UI", 10, "bold") if bold else ("Segoe UI", 10)
    btn = tk.Button(
        parent, text=text, font=font, bg=bg, fg=fg,
        activebackground=active_bg, activeforeground=active_fg,
        relief="flat", padx=8, pady=8, cursor="hand2", command=command,
    )
    btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=pack_padx)
    return btn


def build_countdown_ui(win) -> None:
    """Construct all Tkinter widgets and attach references onto CountdownWindow."""
    bg_dark, card_bg, border = PALETTE["bg_dark"], PALETTE["card_bg"], PALETTE["card_border"]
    win.title("Smart Shutdown")
    win.configure(bg=bg_dark)

    badge_frame = tk.Frame(win, bg=bg_dark)
    badge_frame.pack(fill=tk.X, padx=20, pady=(15, 5))
    badge_text, badge_color = resolve_mode_badge(win.dry_run, win.skip_shutdown)
    win.lbl_badge = tk.Label(badge_frame, text=badge_text, font=("Segoe UI", 10, "bold"), bg=bg_dark, fg=badge_color)
    win.lbl_badge.pack(anchor="center")

    tk.Label(win, text="Smart Shutdown", font=("Segoe UI", 15, "bold"), bg=bg_dark, fg=PALETTE["text_white"]).pack(pady=(2, 10))

    banner_card = tk.Frame(win, bg=card_bg, highlightbackground=border, highlightthickness=1)
    banner_card.pack(fill=tk.X, padx=25, pady=5)
    win.lbl_banner_en = tk.Label(banner_card, text=BANNER_COMPLETE_EN, font=("Segoe UI", 11, "bold"), bg=card_bg, fg=PALETTE["text_white"], justify="center")
    win.lbl_banner_en.pack(padx=15, pady=(12, 4))
    win.lbl_banner_hi = tk.Label(banner_card, text=BANNER_COMPLETE_HI, font=("Segoe UI", 9), bg=card_bg, fg=PALETTE["text_dim"], justify="center")
    win.lbl_banner_hi.pack(padx=15, pady=(0, 12))

    timer_card = tk.Frame(win, bg=card_bg, highlightbackground=border, highlightthickness=1)
    timer_card.pack(fill=tk.X, padx=25, pady=8)
    win.lbl_timer = tk.Label(timer_card, text=format_countdown_time(win.remaining_seconds), font=("Consolas", 46, "bold"), bg=card_bg, fg=PALETTE["accent_blue"])
    win.lbl_timer.pack(pady=(10, 2))
    win.lbl_timer_sub = tk.Label(timer_card, text="Autonomous system shutdown countdown", font=("Segoe UI", 9), bg=card_bg, fg=PALETTE["text_dim"])
    win.lbl_timer_sub.pack(pady=(0, 8))
    win.canvas_progress = tk.Canvas(timer_card, width=540, height=10, bg=border, highlightthickness=0)
    win.canvas_progress.pack(pady=(0, 12))
    win.rect_progress = win.canvas_progress.create_rectangle(0, 0, 540, 10, fill=PALETTE["accent_blue"], width=0)

    summary_text = truncate_text(win.summary_info or "System verified quiet and stable. No active tasks remain.", 80)
    win.lbl_context = tk.Label(win, text=f"Status: {summary_text}", font=("Segoe UI", 8), bg=bg_dark, fg=PALETTE["text_dim"])
    win.lbl_context.pack(pady=(2, 10))

    btn_frame = tk.Frame(win, bg=bg_dark)
    btn_frame.pack(fill=tk.X, padx=18, pady=(0, 15))
    dark_fg = PALETTE["btn_dark_fg"]
    win.btn_cancel = _create_action_button(btn_frame, "❌ Cancel", PALETTE["accent_red"], dark_fg, "#e78284", dark_fg, win.on_cancel, True, (0, 3))
    win.btn_pause = _create_action_button(btn_frame, "⏸️ Pause", "#45475a", PALETTE["text_white"], "#585b70", "#ffffff", win.on_toggle_pause, False, 3)
    win.btn_reset = _create_action_button(btn_frame, "🔄 Reset", PALETTE["accent_cyan"], dark_fg, "#74c7ec", dark_fg, win.on_reset_timer, True, 3)
    win.btn_reset.bind("<Enter>", lambda e: win.btn_reset.configure(bg="#74c7ec"))
    win.btn_reset.bind("<Leave>", lambda e: win.btn_reset.configure(bg=PALETTE["accent_cyan"]))
    win.btn_shutdown = _create_action_button(btn_frame, "⚡ Shutdown Now", "#fab387", dark_fg, "#f5a97f", dark_fg, win.on_shutdown_now, True, (3, 0))
