# -*- coding: utf-8 -*-
"""
core.win32_window: Win32 window Z-order and topmost management utilities.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import ctypes


def make_hwnd_topmost(hwnd: int) -> bool:
    """Set HWND_TOPMOST flag on window handle to stay above exclusive fullscreen video."""
    try:
        hwnd_topmost = -1
        swp_nomove = 0x0002
        swp_nosize = 0x0001
        swp_showwindow = 0x0040
        flags = swp_nomove | swp_nosize | swp_showwindow
        res = ctypes.windll.user32.SetWindowPos(hwnd, hwnd_topmost, 0, 0, 0, 0, flags)
        return bool(res)
    except Exception:
        return False


__all__ = ["make_hwnd_topmost"]
