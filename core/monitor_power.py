# -*- coding: utf-8 -*-
"""
core.monitor_power: Windows DPMS API Display Sleep Utility.
Uses Win32 SendMessageW to put display(s) to sleep safely without suspending the PC.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import ctypes
import logging

logger = logging.getLogger("SmartShutdown")

HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170
MONITOR_OFF = 2


def toggle_monitor_power_off() -> bool:
    """Put all connected monitors to sleep via Windows DPMS API."""
    try:
        # Primary: ctypes user32 SendMessageW
        ctypes.windll.user32.SendMessageW(
            HWND_BROADCAST,
            WM_SYSCOMMAND,
            SC_MONITORPOWER,
            MONITOR_OFF,
        )
        logger.info("[DPMS] Monitor power off command dispatched successfully via ctypes.")
        return True
    except Exception as e:
        logger.warning(f"[DPMS] ctypes dispatch failed ({e}), attempting win32gui fallback.")
        try:
            import win32gui
            try:
                import win32con
            except ImportError:
                win32con = None

            win32gui.SendMessage(
                getattr(win32con, "HWND_BROADCAST", HWND_BROADCAST),
                getattr(win32con, "WM_SYSCOMMAND", WM_SYSCOMMAND),
                getattr(win32con, "SC_MONITORPOWER", SC_MONITORPOWER),
                MONITOR_OFF,
            )
            logger.info("[DPMS] Monitor power off command dispatched successfully via win32gui fallback.")
            return True
        except Exception as fallback_err:
            logger.error(f"[DPMS] Failed to toggle monitor power off: {fallback_err}")
            return False
