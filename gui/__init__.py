# -*- coding: utf-8 -*-
"""
gui: Modern Fluent Dark Desktop GUI, Single Unified Application & Countdown Overlay.
Legacy unused exports use PEP 562 lazy loading to keep Combined GUI startup clean.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import importlib
from typing import Any, Dict, List, Tuple

from core.config import SettingsConfig
from gui.dialogs.close_confirm_dialog import CloseConfirmDialog
from gui.components.mini_overlay import FloatingMiniOverlay
from gui.unified_app import (
    UnifiedSentinelApp,
    launch_unified_gui,
)

_LAZY_EXPORTS: Dict[str, Tuple[str, str]] = {
    "SettingsWindow": ("gui.settings_window", "SettingsWindow"),
    "BG_BASE": ("gui.settings_window", "BG_BASE"),
    "BG_SURFACE": ("gui.settings_window", "BG_SURFACE"),
    "ACCENT_COLOR": ("gui.settings_window", "ACCENT_COLOR"),
    "WARN_COLOR": ("gui.settings_window", "WARN_COLOR"),
    "TEXT_PRIMARY": ("gui.settings_window", "TEXT_PRIMARY"),
    "TEXT_SECONDARY": ("gui.settings_window", "TEXT_SECONDARY"),
    "BORDER_COLOR": ("gui.settings_window", "BORDER_COLOR"),
    "STATUS_GREEN": ("gui.settings_window", "STATUS_GREEN"),
    "STATUS_YELLOW": ("gui.settings_window", "STATUS_YELLOW"),
    "STATUS_RED": ("gui.settings_window", "STATUS_RED"),
    "CountdownOverlay": ("gui.countdown_overlay", "CountdownOverlay"),
    "get_last_input_tick": ("gui.countdown_overlay", "get_last_input_tick"),
    "make_hwnd_topmost": ("core.win32_window", "make_hwnd_topmost"),
    "TelemetryCardsDeck": ("gui.components.telemetry_cards", "TelemetryCardsDeck"),
    "SettingsDeck": ("gui.components.settings_deck", "SettingsDeck"),
    "DiagnosticTerminal": ("gui.components.log_terminal", "DiagnosticTerminal"),
}

__all__ = [
    "SettingsConfig",
    "SettingsWindow",
    "CloseConfirmDialog",
    "CountdownOverlay",
    "make_hwnd_topmost",
    "get_last_input_tick",
    "UnifiedSentinelApp",
    "launch_unified_gui",
    "TelemetryCardsDeck",
    "SettingsDeck",
    "DiagnosticTerminal",
    "FloatingMiniOverlay",
    "BG_BASE",
    "BG_SURFACE",
    "ACCENT_COLOR",
    "WARN_COLOR",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "BORDER_COLOR",
    "STATUS_GREEN",
    "STATUS_YELLOW",
    "STATUS_RED",
]


def __getattr__(name: str) -> Any:
    """Resolve legacy GUI and constant exports lazily per PEP 562."""
    if name in _LAZY_EXPORTS:
        module_name, attr_name = _LAZY_EXPORTS[name]
        module = importlib.import_module(module_name)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    """Expose full backward-compatible __all__ symbols for dir()."""
    return sorted(set(globals()) | set(__all__))
