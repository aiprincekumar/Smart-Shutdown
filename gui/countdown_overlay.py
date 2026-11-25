# -*- coding: utf-8 -*-
"""
gui.countdown_overlay: Modern HWND_TOPMOST Floating Countdown Overlay.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import ctypes
from ctypes import wintypes
import tkinter as tk
from typing import Callable, Optional

# Palette Constants (Fluent Dark)
BG_BASE = "#1E1E24"
BG_SURFACE = "#2B2B36"
ACCENT_COLOR = "#0078D4"
WARN_COLOR = "#FF8C00"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0A0"
BORDER_COLOR = "#3A3A48"
STATUS_RED = "#D83B01"
FONT_FAMILY = "Segoe UI"


class LASTINPUTINFO(ctypes.Structure):
    """Windows LASTINPUTINFO structure for tracking physical hardware input."""
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_last_input_tick() -> int:
    """Retrieve physical hardware input tick count via Win32 GetLastInputInfo."""
    try:
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            return int(lii.dwTime)
    except Exception:
        pass
    return 0


from core.win32_window import make_hwnd_topmost


class CountdownOverlay(tk.Toplevel):
    """
    Topmost Floating Banner Overlay (320px x 140px) at top-right of screen.
    Displays big digital timer (MM:SS) with Pause, Resume, and Cancel buttons.
    Hooks physical mouse motion and keystrokes to immediately reset to Step 1.
    """

    def __init__(
        self,
        parent: Optional[tk.Tk] = None,
        countdown_seconds: int = 900,
        auto_start: bool = True,
        on_pause: Optional[Callable[[], None]] = None,
        on_resume: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        on_timeout: Optional[Callable[[], None]] = None,
        countdown_sec: Optional[int] = None,
    ):
        if countdown_sec is not None:
            countdown_seconds = countdown_sec

        self._owned_root = None
        if parent is None:
            self._owned_root = tk.Tk()
            self._owned_root.withdraw()
            parent = self._owned_root

        super().__init__(parent)
        self.countdown_seconds = int(countdown_seconds)
        self.remaining_seconds = int(countdown_seconds)
        self.auto_start = auto_start
        self.on_pause_callback = on_pause
        self.on_resume_callback = on_resume
        self.on_cancel_callback = on_cancel
        self.on_reset_callback = on_reset
        self.on_timeout_callback = on_timeout

        self.is_paused = False
        self.is_cancelled = False
        self._timer_job = None
        self._input_job = None
        self.baseline_input_tick = get_last_input_tick()

        self._setup_window()
        self._build_ui()
        self._enforce_topmost()
        self._bind_physical_input_hooks()
        if self.auto_start:
            self._start_timer()
            self._start_input_poller()

    def _setup_window(self) -> None:
        """Configure borderless geometry at top-right of primary screen."""
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=WARN_COLOR)

        sw = self.winfo_screenwidth()
        width, height = 320, 140
        x = max(0, sw - width - 24)
        y = 24
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self) -> None:
        """Construct inner card, digital timer display, and interactive buttons."""
        inner = tk.Frame(self, bg=BG_SURFACE, padx=10, pady=8)
        inner.pack(fill="both", expand=True, padx=2, pady=2)

        hdr_row = tk.Frame(inner, bg=BG_SURFACE)
        hdr_row.pack(fill="x")

        lbl_title = tk.Label(
            hdr_row,
            text="⚡ Smart Shutdown Warning",
            font=(FONT_FAMILY, 9, "bold"),
            fg=WARN_COLOR,
            bg=BG_SURFACE,
        )
        lbl_title.pack(side="left")

        self.timer_label = tk.Label(
            inner,
            text=self.format_time(self.remaining_seconds),
            font=(FONT_FAMILY, 24, "bold"),
            fg=WARN_COLOR,
            bg=BG_SURFACE,
        )
        self.timer_label.pack(pady=(0, 1))

        self.status_label = tk.Label(
            inner,
            text="System idle. Shutdown imminent...",
            font=(FONT_FAMILY, 8),
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE,
        )
        self.status_label.pack(pady=(0, 6))

        self._build_button_row(inner)

    def _build_button_row(self, parent: tk.Frame) -> None:
        """Create Pause, Resume, and Cancel buttons."""
        btn_bar = tk.Frame(parent, bg=BG_SURFACE)
        btn_bar.pack(fill="x")

        self.btn_pause = tk.Button(
            btn_bar,
            text="⏸️ Pause",
            font=(FONT_FAMILY, 8, "bold"),
            bg=BG_BASE,
            fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=8,
            pady=3,
            command=self.pause,
        )
        self.btn_pause.pack(side="left", expand=True, padx=2)

        self.btn_resume = tk.Button(
            btn_bar,
            text="▶️ Resume",
            font=(FONT_FAMILY, 8, "bold"),
            bg=BG_BASE,
            fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=8,
            pady=3,
            command=self.resume,
        )
        self.btn_resume.pack(side="left", expand=True, padx=2)

        btn_cancel = tk.Button(
            btn_bar,
            text="❌ Cancel",
            font=(FONT_FAMILY, 8, "bold"),
            bg=STATUS_RED,
            fg=TEXT_PRIMARY,
            activebackground="#E81123",
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=8,
            pady=3,
            command=self.cancel,
        )
        btn_cancel.pack(side="right", expand=True, padx=2)

    def _enforce_topmost(self) -> None:
        """Apply HWND_TOPMOST via Windows Win32 API and Tkinter."""
        self.lift()
        self.attributes("-topmost", True)
        try:
            hwnd = self.winfo_id()
            make_hwnd_topmost(hwnd)
        except Exception:
            pass

    def _bind_physical_input_hooks(self) -> None:
        """Bind local keyboard and mouse events to reset workflow."""
        self.bind("<Motion>", self._on_local_input)
        self.bind("<Key>", self._on_local_input)

    def _on_local_input(self, event=None) -> None:
        """Local window event handler triggering physical input reset."""
        self.trigger_physical_input_reset()

    def _start_timer(self) -> None:
        """Schedule periodic 1-second countdown tick."""
        self._timer_job = self.after(1000, self._timer_tick)

    def _timer_tick(self) -> None:
        """Decrement remaining time when not paused."""
        if self.is_cancelled:
            return

        if not self.is_paused:
            self.remaining_seconds = max(0, self.remaining_seconds - 1)
            self.timer_label.config(text=self.format_time(self.remaining_seconds))

            if self.remaining_seconds <= 0:
                self._handle_timeout()
                return

        self._timer_job = self.after(1000, self._timer_tick)

    def _start_input_poller(self) -> None:
        """Schedule physical hardware input tick polling every 300ms."""
        self._input_job = self.after(300, self._poll_physical_input)

    def _poll_physical_input(self) -> None:
        """Poll Windows GetLastInputInfo to detect any mouse or keyboard action."""
        if self.is_cancelled:
            return

        curr_tick = get_last_input_tick()
        if self.check_physical_input(curr_tick):
            return

        self._input_job = self.after(300, self._poll_physical_input)

    def check_physical_input(self, current_tick: Optional[int] = None) -> bool:
        """Check if physical hardware input tick changed since baseline."""
        curr = current_tick if current_tick is not None else get_last_input_tick()
        if self.baseline_input_tick > 0 and curr > self.baseline_input_tick:
            self.trigger_physical_input_reset(curr)
            return True
        return False

    def trigger_physical_input_reset(self, tick: Optional[int] = None) -> None:
        """Trigger abort and reset back to Step 1 due to physical user activity."""
        self.status_label.config(text="Physical input detected! Resetting...")
        self.cancel_timer_jobs()
        if self.on_reset_callback:
            self.on_reset_callback()
        self.close()

    def _handle_timeout(self) -> None:
        """Handle countdown reaching 00:00."""
        self.status_label.config(text="Shutdown initiated...")
        self.cancel_timer_jobs()
        if self.on_timeout_callback:
            self.on_timeout_callback()

    def pause(self) -> None:
        """Pause countdown timer."""
        self.is_paused = True
        self.status_label.config(text="⏸️ Countdown Paused by User")
        self.timer_label.config(fg=TEXT_SECONDARY)
        if self.on_pause_callback:
            self.on_pause_callback()

    def resume(self) -> None:
        """Resume countdown timer."""
        self.is_paused = False
        self.status_label.config(text="System idle. Shutdown imminent...")
        self.timer_label.config(fg=WARN_COLOR)
        self.baseline_input_tick = get_last_input_tick()
        if self.on_resume_callback:
            self.on_resume_callback()

    def cancel(self) -> None:
        """Cancel countdown and abort shutdown sequence."""
        self.is_cancelled = True
        self.status_label.config(text="❌ Shutdown sequence cancelled.")
        self.cancel_timer_jobs()
        if self.on_cancel_callback:
            self.on_cancel_callback()
        self.close()

    def cancel_timer_jobs(self) -> None:
        """Cancel pending Tkinter after callbacks."""
        if self._timer_job:
            try:
                self.after_cancel(self._timer_job)
            except Exception:
                pass
            self._timer_job = None
        if self._input_job:
            try:
                self.after_cancel(self._input_job)
            except Exception:
                pass
            self._input_job = None

    def close(self) -> None:
        """Safely close and destroy overlay window."""
        self.cancel_timer_jobs()
        try:
            self.update_idletasks()
            self.destroy()
        except Exception:
            pass
        if self._owned_root:
            try:
                self._owned_root.update_idletasks()
                self._owned_root.destroy()
            except Exception:
                pass
            self._owned_root = None

    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds into MM:SS string display."""
        total_sec = max(0, int(seconds))
        mins = total_sec // 60
        secs = total_sec % 60
        return f"{mins:02d}:{secs:02d}"


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    overlay = CountdownOverlay(parent=root, countdown_seconds=20)
    root.mainloop()
