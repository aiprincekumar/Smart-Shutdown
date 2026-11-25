# -*- coding: utf-8 -*-
"""
core.input_hook: Physical user inactivity tracking via Win32 GetLastInputInfo.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

Provides physical keystroke and mouse movement monitoring with strict media
playback immunity (video players / YouTube do not update hardware input ticks).
"""

import sys
import time
import ctypes
from ctypes import wintypes
from typing import Optional

# Win32 Structure for tracking last user input
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD)
    ]

# Internal Win32 function pointers (loaded lazily / safely)
_user32 = None
_kernel32 = None

def _get_user32():
    """Lazily loads and returns the user32 DLL on Windows."""
    global _user32
    if _user32 is None and sys.platform == "win32":
        _user32 = ctypes.windll.user32
    return _user32

def _get_kernel32():
    """Lazily loads and returns the kernel32 DLL on Windows."""
    global _kernel32
    if _kernel32 is None and sys.platform == "win32":
        _kernel32 = ctypes.windll.kernel32
    return _kernel32

def get_last_input_tick() -> int:
    """
    Retrieves the millisecond tick count of the last physical input event
    (keystroke, mouse movement, mouse button click).
    
    Returns:
        int: Tick count in milliseconds from system boot.
    """
    user32 = _get_user32()
    if not user32:
        return int(time.time() * 1000)

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    success = user32.GetLastInputInfo(ctypes.byref(lii))
    if not success:
        return int(time.time() * 1000)
    return int(lii.dwTime)

def get_system_uptime_ms() -> int:
    """
    Retrieves the total system uptime in milliseconds.
    Prefers GetTickCount64 to avoid 49.7-day rollover; falls back to GetTickCount.
    
    Returns:
        int: Uptime in milliseconds.
    """
    kernel32 = _get_kernel32()
    if not kernel32:
        return int(time.time() * 1000)

    if hasattr(kernel32, "GetTickCount64"):
        return int(kernel32.GetTickCount64())
    return int(kernel32.GetTickCount())

def get_idle_seconds() -> float:
    """
    Calculates elapsed physical user idle time in seconds.
    Physical inactivity timer is immune to background audio and video playback.
    
    Returns:
        float: Elapsed idle time in seconds (clamped to >= 0.0).
    """
    uptime_ms = get_system_uptime_ms()
    last_input_tick = get_last_input_tick()

    # 32-bit tick count rollover handling (wraps at 0xFFFFFFFF ~ 49.7 days)
    diff_ms = (uptime_ms & 0xFFFFFFFF) - (last_input_tick & 0xFFFFFFFF)
    if diff_ms < 0:
        diff_ms += 0x100000000

    return max(0.0, diff_ms / 1000.0)

def is_user_idle(threshold_seconds: float = 60.0) -> bool:
    """
    Determines whether the user has been physically inactive for at least
    the specified threshold in seconds.
    
    Args:
        threshold_seconds: Required period of inactivity (default: 60.0s).
        
    Returns:
        bool: True if idle elapsed time >= threshold_seconds, False otherwise.
    """
    return get_idle_seconds() >= max(0.0, float(threshold_seconds))

def get_last_input_timestamp() -> float:
    """
    Estimates the absolute epoch timestamp (seconds) of the last physical input.
    
    Returns:
        float: Absolute UNIX timestamp of last input.
    """
    return time.time() - get_idle_seconds()


# Semantic Alias for Dual-Timer Telemetry Invariant
def get_user_idle_seconds() -> float:
    return get_idle_seconds()


