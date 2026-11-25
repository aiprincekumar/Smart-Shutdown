# -*- coding: utf-8 -*-
"""
core.models: Domain data models and lifecycle state definitions for Smart Shutdown.
Universal Rule 28 Architectural Modularity Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class LifecycleState(str, Enum):
    """Lifecycle states of Smart Shutdown."""
    IDLE_MONITORING = "IDLE_MONITORING"           # Step 1: Tracking user physical inactivity
    AI_EVALUATION = "AI_EVALUATION"               # Step 2: Evaluating AntiGravity transcripts & child processes
    WAITING_USER_PROMPT = "WAITING_USER_PROMPT"   # Step 2b: Awaiting interactive user reply (grill-me)
    COUNTDOWN_ACTIVE = "COUNTDOWN_ACTIVE"         # Step 3: Master countdown timer running
    PRE_SHUTDOWN_GRACE = "PRE_SHUTDOWN_GRACE"     # Step 4: Final grace window (app closer triggered)
    SHUTDOWN_EXECUTED = "SHUTDOWN_EXECUTED"       # Step 5: Shutdown command dispatched
    ABORTED_RESET = "ABORTED_RESET"               # Interrupted: Reset back to Step 1


class TargetMode(str, Enum):
    """Execution mode of the shutdown sentinel."""
    LIVE = "LIVE"
    DEMO_30S = "DEMO (30s)"
    SIMULATION = "SIMULATION"
    DEMO_10S = "DEMO (10s)"  # Backward-compatible alias


DEFAULT_SIMULATION_SECONDS = 300


def resolve_mode_duration_seconds(
    mode: TargetMode,
    master_shutdown_timer_min: int,
    simulation_timer_sec: int = DEFAULT_SIMULATION_SECONDS,
) -> int:
    """Return default countdown duration in seconds for the given TargetMode."""
    if mode == TargetMode.DEMO_30S:
        return 30
    if mode == TargetMode.DEMO_10S:
        return 10
    if mode == TargetMode.SIMULATION:
        return max(10, int(simulation_timer_sec))
    return int(master_shutdown_timer_min * 60)


class AntiGravityAIState(str, Enum):
    """Priority-driven status of AntiGravity AI engine."""
    INPUT_PENDING = "WAITING"
    WORKING = "WORKING"
    BUSY = "BUSY"
    READY = "READY"


@dataclass
class TelemetryEvent:
    """Telemetry message pushed to UI main thread."""
    event_type: str  # 'STATE_CHANGE', 'TICK', 'TELEMETRY', 'LOG', 'SHUTDOWN', 'AI_STATE_CHANGE', etc.
    timestamp: float
    data: Dict[str, Any]


@dataclass
class UserCommand:
    """User command sent from UI to coordinator."""
    command_type: str  # 'PAUSE', 'RESUME', 'CANCEL', 'SNOOZE', 'FORCE_SHUTDOWN', 'UPDATE_CONFIG', 'SET_MODE'
    payload: Optional[Dict[str, Any]] = None


__all__ = [
    "LifecycleState",
    "TargetMode",
    "DEFAULT_SIMULATION_SECONDS",
    "resolve_mode_duration_seconds",
    "AntiGravityAIState",
    "TelemetryEvent",
    "UserCommand",
]
