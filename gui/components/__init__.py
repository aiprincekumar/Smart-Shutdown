# -*- coding: utf-8 -*-
"""
gui.components: Modular UI components for Single Unified Sentinel Desktop Application.
Legacy unused decks use PEP 562 lazy loading to avoid eager startup imports.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import importlib
from typing import Any, Dict, List, Tuple

from gui.components.mini_overlay import FloatingMiniOverlay
from gui.components.title_bar import (
    TitleBarComponent,
    AntiGravityAIState,
    SentinelState,
    TargetMode,
)
from gui.components.dashboard_view import DashboardView
from gui.components.circular_gauge import CircularCountdownGauge
from gui.components.pill_button import PillButton
from gui.components.sparklines import CanvasSparkline
from gui.components.telemetry_view import TelemetryView
from gui.components.logs_view import LogsView
from gui.components.history_view import HistoryView
from gui.components.settings_view import SettingsView

_LAZY_EXPORTS: Dict[str, Tuple[str, str]] = {
    "TelemetryCardsDeck": ("gui.components.telemetry_cards", "TelemetryCardsDeck"),
    "SettingsDeck": ("gui.components.settings_deck", "SettingsDeck"),
    "DiagnosticTerminal": ("gui.components.log_terminal", "DiagnosticTerminal"),
}

__all__ = [
    "TelemetryCardsDeck",
    "SettingsDeck",
    "DiagnosticTerminal",
    "FloatingMiniOverlay",
    "TitleBarComponent",
    "AntiGravityAIState",
    "SentinelState",
    "TargetMode",
    "DashboardView",
    "CircularCountdownGauge",
    "PillButton",
    "CanvasSparkline",
    "TelemetryView",
    "LogsView",
    "HistoryView",
    "SettingsView",
]


def __getattr__(name: str) -> Any:
    """Resolve legacy component exports lazily per PEP 562."""
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
