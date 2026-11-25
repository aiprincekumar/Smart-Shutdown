# -*- coding: utf-8 -*-
"""
core.audio: Non-blocking audio alerts and WASAPI active stream detection.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import time
import threading
import winsound
from typing import Any


def play_sound_alert(repeats: int = 2, delay: float = 0.5):
    """Plays Windows warning chime in a non-blocking daemon thread."""
    def _play():
        for _ in range(repeats):
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                try:
                    winsound.Beep(1000, 300)
                except Exception:
                    pass
            time.sleep(delay)

    t = threading.Thread(target=_play, daemon=True)
    t.start()


def play_tick_sound():
    """Plays a short tick during final countdown seconds."""
    def _tick():
        try:
            winsound.Beep(1400, 80)
        except Exception:
            pass

    t = threading.Thread(target=_tick, daemon=True)
    t.start()


def play_reset_sound():
    """Plays clean audio feedback when timer is reset."""
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


def _is_session_playing(
    session: Any,
    peak_threshold: float = 0.001,
    meter_iface: Any = None,
) -> bool:
    """Inspect a single WASAPI AudioSession for active non-zero audio playback."""
    try:
        if getattr(session, "ProcessId", 1) == 0:
            return False
        if getattr(session, "State", None) != 1:
            return False
        ctl = getattr(session, "_ctl", None)
        if ctl is None:
            return False
        if meter_iface is None:
            from pycaw.pycaw import IAudioMeterInformation
            meter_iface = IAudioMeterInformation
        meter = ctl.QueryInterface(meter_iface)
        peak = meter.GetPeakValue()
        return isinstance(peak, (int, float)) and float(peak) > peak_threshold
    except Exception:
        return False


def is_audio_stream_active(peak_threshold: float = 0.001) -> bool:
    """Return True if any non-system WASAPI audio session is actively outputting sound."""
    try:
        import comtypes
        from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
    except Exception:
        return False

    com_initialized = False
    try:
        try:
            comtypes.CoInitialize()
            com_initialized = True
        except OSError:
            com_initialized = False

        sessions = AudioUtilities.GetAllSessions() or []
        return any(
            _is_session_playing(session, peak_threshold, IAudioMeterInformation)
            for session in sessions
        )
    except Exception:
        return False
    finally:
        if com_initialized:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass
