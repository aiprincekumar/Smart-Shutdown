# -*- coding: utf-8 -*-
"""
core.gui: Smart Shutdown Always-On-Top Countdown Window with interactive controls & live session monitor.
Universal Rule 28 Architectural Modularity Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import time
import threading
import logging
import winsound
import tkinter as tk
from core.config import (
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    log_telemetry_event,
    release_single_instance_lock,
)
from core.console import hide_console_window
from core.audio import play_sound_alert, play_tick_sound
from core.killer import force_close_all_apps
from core.shutdown import execute_system_shutdown
from core.analyzer import AntigravitySessionAnalyzer
from core.gui_widgets import (
    PALETTE,
    apply_pause_button_style,
    build_countdown_ui,
    format_countdown_time,
    resolve_auto_pause_badge,
    resolve_mode_badge,
    set_banner_text,
    truncate_text,
)


class CountdownWindow(tk.Tk):
    """Always-on-top interactive countdown window with live Antigravity task monitoring."""

    def __init__(
        self,
        countdown_seconds: int = DEFAULT_COUNTDOWN_SECONDS,
        dry_run: bool = False,
        skip_shutdown: bool = False,
        summary_info: str = "",
        analyzer: AntigravitySessionAnalyzer = None,
        idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS,
        logger=None,
    ):
        super().__init__()
        self.countdown_seconds = int(countdown_seconds)
        self.remaining_seconds = int(countdown_seconds)
        self.dry_run = dry_run
        self.skip_shutdown = skip_shutdown
        self.summary_info = summary_info
        self.analyzer = analyzer
        self.idle_buffer = int(idle_buffer)
        self.logger = logger or logging.getLogger("SmartShutdown")

        self.user_paused = False
        self.auto_paused = False
        self.auto_pause_reason = ""
        self.cancelled = False
        self.shutdown_triggered = False
        self.force_close_triggered = False
        self._monitor_active = True

        hide_console_window(self.logger)
        self._build_ui()
        self._center_window(680, 520)

        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        play_sound_alert(repeats=2, delay=0.5)
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._start_live_task_monitor()
        self._timer_after_id = self.after(1000, self._timer_tick)

    @property
    def is_paused(self) -> bool:
        """True if paused manually by user or auto-paused by live Antigravity task activity."""
        return self.user_paused or self.auto_paused

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts for cancel, shutdown, pause, and reset."""
        bindings = {
            "<Escape>": self.on_cancel, "c": self.on_cancel, "C": self.on_cancel,
            "<Return>": self.on_shutdown_now, "s": self.on_shutdown_now, "S": self.on_shutdown_now,
            "<space>": self.on_toggle_pause, "p": self.on_toggle_pause, "P": self.on_toggle_pause,
            "r": self.on_reset_timer, "R": self.on_reset_timer,
        }
        for key, handler in bindings.items():
            self.bind(key, lambda _e, fn=handler: fn())

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

    def _build_ui(self) -> None:
        build_countdown_ui(self)

    def _format_time(self, seconds: int) -> str:
        return format_countdown_time(seconds)

    def _update_progress(self) -> None:
        fraction = max(0.0, min(1.0, self.remaining_seconds / max(1, self.countdown_seconds)))
        self.canvas_progress.coords(self.rect_progress, 0, 0, int(540 * fraction), 10)

        if self.auto_paused or self.user_paused:
            color = PALETTE["accent_amber"]
        elif self.remaining_seconds <= 10:
            color = PALETTE["accent_red"]
        elif self.remaining_seconds <= 60:
            color = PALETTE["accent_amber"]
        else:
            color = PALETTE["accent_blue"]

        self.lbl_timer.configure(fg=color)
        self.canvas_progress.itemconfig(self.rect_progress, fill=color)
        try:
            self.canvas_progress.update_idletasks()
        except Exception:
            pass

    def _start_live_task_monitor(self) -> None:
        """Inspect Antigravity sessions continuously on a daemon thread and auto-pause/resume."""
        if not self.analyzer:
            return

        try:
            initial_eval = self.analyzer.evaluate_all(idle_buffer=self.idle_buffer)
            self._handle_task_evaluation(initial_eval)
        except Exception as exc:
            self.logger.debug(f"[INITIAL_INSPECT_ERROR] Initial evaluation failed: {exc}")

        def _monitor_worker() -> None:
            while self._monitor_active and not self.cancelled and not self.shutdown_triggered:
                time.sleep(1.2)
                if not self._monitor_active or self.cancelled or self.shutdown_triggered:
                    break
                try:
                    eval_res = self.analyzer.evaluate_all(idle_buffer=self.idle_buffer)
                    if self._monitor_active and not self.cancelled and not self.shutdown_triggered:
                        self.after(0, self._handle_task_evaluation, eval_res)
                except Exception as exc:
                    self.logger.debug(f"[LIVE_MONITOR_ERROR] Session evaluation exception: {exc}")

        threading.Thread(target=_monitor_worker, daemon=True).start()

    def _update_context_summary(self, summary: str) -> None:
        if summary:
            self.lbl_context.configure(text=f"Status: {truncate_text(summary, 80)}")

    def _apply_busy_task_state(self, eval_res: dict) -> None:
        """Handle active Antigravity task/command blocking by auto-pausing the countdown."""
        blocking_reason = eval_res.get("blocking_reason") or "Antigravity command/task in progress"
        disp_reason = truncate_text(blocking_reason, 55)

        if not self.auto_paused:
            self.auto_paused = True
            self.auto_pause_reason = disp_reason
            log_telemetry_event(self.logger, "AUTO_PAUSED_BUSY_TASK", {
                "reason": blocking_reason,
                "blocking_session": eval_res.get("blocking_session"),
                "remaining_seconds": self.remaining_seconds,
            })
            self.logger.info(f"[AUTO_PAUSE] ⏸️ Auto-paused countdown: {blocking_reason}")

        self.auto_pause_reason = disp_reason
        set_banner_text(self, active_task=True)
        self.lbl_badge.configure(text=resolve_auto_pause_badge(blocking_reason), fg=PALETTE["accent_amber"])

        if not self.user_paused:
            self.lbl_timer_sub.configure(text=f"⏸️ AUTO-PAUSED: {disp_reason}", fg=PALETTE["accent_amber"])
            apply_pause_button_style(self.btn_pause, "auto_paused")

        self._update_progress()
        self._update_context_summary(eval_res.get("summary", ""))

    def _apply_completed_task_state(self, eval_res: dict) -> None:
        """Auto-resume countdown and restore completion banners when all tasks finish."""
        if self.auto_paused:
            self.auto_paused = False
            self.auto_pause_reason = ""
            log_telemetry_event(self.logger, "AUTO_RESUMED_TASKS_COMPLETE", {"remaining_seconds": self.remaining_seconds})
            self.logger.info("[AUTO_RESUME] ▶️ Auto-resumed countdown: All Antigravity tasks completed.")

            set_banner_text(self, active_task=False)
            badge_text, badge_color = resolve_mode_badge(self.dry_run, self.skip_shutdown)
            self.lbl_badge.configure(text=badge_text, fg=badge_color)

            if not self.user_paused:
                self.lbl_timer_sub.configure(
                    text="▶️ Resumed: Antigravity tasks completed. Countdown continuing...",
                    fg=PALETTE["accent_green"],
                )
                apply_pause_button_style(self.btn_pause, "pause")
                self.after(4000, self._reset_resumed_label)

            self._update_progress()

        self._update_context_summary(eval_res.get("summary", ""))

    def _handle_task_evaluation(self, eval_res: dict) -> None:
        """Process live session evaluation on the Tkinter main thread."""
        if not self._monitor_active or self.cancelled or self.shutdown_triggered:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        if not eval_res.get("all_completed", True):
            self._apply_busy_task_state(eval_res)
        else:
            self._apply_completed_task_state(eval_res)

    def _reset_resumed_label(self) -> None:
        """Restore default countdown subtitle 4 seconds after resume/reset."""
        try:
            if not self.is_paused and not self.force_close_triggered and not self.cancelled and not self.shutdown_triggered and self.winfo_exists():
                self.lbl_timer_sub.configure(text="Autonomous system shutdown countdown", fg=PALETTE["text_dim"])
        except Exception:
            pass

    def _timer_tick(self) -> None:
        if self.cancelled or self.shutdown_triggered:
            return

        if not self.is_paused:
            self.remaining_seconds -= 1
            self.lbl_timer.configure(text=self._format_time(self.remaining_seconds))
            self._update_progress()

            if self.remaining_seconds <= 10 and not self.force_close_triggered:
                self.force_close_triggered = True
                self.lbl_timer_sub.configure(text="⚠️ T-10s: Force closing all open apps & windows...", fg=PALETTE["accent_red"])
                threading.Thread(target=force_close_all_apps, kwargs={"dry_run": self.dry_run, "logger": self.logger}, daemon=True).start()

            if 0 < self.remaining_seconds <= 10:
                play_tick_sound()

            if self.remaining_seconds <= 0:
                self.on_timer_expired()
                return

        self._timer_after_id = self.after(1000, self._timer_tick)

    def on_toggle_pause(self) -> None:
        """Toggle manual user pause while honoring active auto-pause blockers on resume."""
        self.user_paused = not self.user_paused
        if self.user_paused:
            apply_pause_button_style(self.btn_pause, "resume")
            self.lbl_timer_sub.configure(text="Timer PAUSED by user. Press Resume to continue.", fg=PALETTE["accent_amber"])
            self.logger.info("[USER_ACTION] Countdown timer paused by user.")
            log_telemetry_event(self.logger, "USER_PAUSED", {"remaining_seconds": self.remaining_seconds})
        else:
            if self.auto_paused:
                apply_pause_button_style(self.btn_pause, "auto_paused")
                self.lbl_timer_sub.configure(
                    text=f"⏸️ AUTO-PAUSED: Antigravity command/task in progress ({self.auto_pause_reason})",
                    fg=PALETTE["accent_amber"],
                )
            else:
                apply_pause_button_style(self.btn_pause, "pause")
                self.lbl_timer_sub.configure(text="Autonomous system shutdown countdown", fg=PALETTE["text_dim"])
            self.logger.info("[USER_ACTION] Countdown timer resumed by user.")
            log_telemetry_event(self.logger, "USER_RESUMED", {"remaining_seconds": self.remaining_seconds})
        self._update_progress()

    def on_reset_timer(self) -> None:
        """Reset countdown timer back to configured countdown_seconds."""
        self.remaining_seconds = self.countdown_seconds
        self.force_close_triggered = False
        formatted = self._format_time(self.countdown_seconds)

        self.lbl_timer.configure(text=self._format_time(self.remaining_seconds))
        self._update_progress()

        if self.user_paused:
            sub_text = f"🔄 Timer reset to {formatted}. Timer is PAUSED (Press Resume to continue)."
        elif self.auto_paused:
            sub_text = f"🔄 Timer reset to {formatted}. (Auto-Paused)"
        else:
            sub_text = f"🔄 Timer reset to {formatted}. Countdown continuing..."
            self.after(4000, self._reset_resumed_label)

        self.lbl_timer_sub.configure(text=sub_text, fg=PALETTE["accent_cyan"])

        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

        self.logger.info(f"[USER_ACTION] Countdown timer reset to {formatted} by user.")
        log_telemetry_event(self.logger, "TIMER_RESET_BY_USER", {
            "countdown_seconds": self.countdown_seconds,
            "remaining_seconds": self.remaining_seconds,
            "is_paused": self.is_paused,
        })

    def on_cancel(self) -> None:
        """Cancel countdown and exit cleanly."""
        self._monitor_active = False
        self.cancelled = True
        self.logger.info("[USER_ACTION] Shutdown CANCELLED by user. Exiting cleanly.")
        play_sound_alert(repeats=1, delay=0.1)
        self.destroy()

    def _execute_shutdown_sequence(self, log_msg: str) -> None:
        self._monitor_active = False
        self.shutdown_triggered = True
        self.logger.info(log_msg)
        if not self.force_close_triggered:
            self.force_close_triggered = True
            force_close_all_apps(dry_run=self.dry_run, logger=self.logger)
        self.destroy()
        execute_system_shutdown(dry_run=self.dry_run, skip_shutdown=self.skip_shutdown, logger=self.logger)

    def on_shutdown_now(self) -> None:
        """Trigger immediate application closure and system shutdown."""
        self._execute_shutdown_sequence("[USER_ACTION] 'Shutdown Now' clicked by user. Executing immediately.")

    def on_timer_expired(self) -> None:
        """Handle countdown reaching zero."""
        self._execute_shutdown_sequence("[TIMER_EXPIRED] Countdown reached 00:00 without user cancellation.")

    def destroy(self) -> None:
        self._monitor_active = False
        release_single_instance_lock(self.logger)
        if getattr(self, "_timer_after_id", None):
            try:
                self.after_cancel(self._timer_after_id)
            except Exception:
                pass
            self._timer_after_id = None
        try:
            super().destroy()
        except Exception:
            pass
