# -*- coding: utf-8 -*-
"""
core.console: Windows console window visibility management (SW_HIDE).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import ctypes

def hide_console_window(logger=None) -> bool:
    """
    Hides the attached Windows console window (SW_HIDE) so only the Tkinter GUI is visible.
    Uses Win32 user32.ShowWindow(kernel32.GetConsoleWindow(), 0).
    """
    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 0)  # 0 = SW_HIDE
            if logger:
                logger.debug("[CONSOLE_HIDDEN] Attached Windows console window successfully hidden (SW_HIDE).")
            return True
    except Exception as e:
        if logger:
            logger.debug(f"[CONSOLE_HIDE_FAILED] Could not hide console window: {e}")
    return False
