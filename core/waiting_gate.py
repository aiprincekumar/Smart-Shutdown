# -*- coding: utf-8 -*-
"""
core.waiting_gate: Tri-modal interactive prompt waiting gate for AntiGravity.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

Implements tri-modal waiting policies (Unlimited, Fixed Timer, Hybrid 10m Default)
to gracefully manage sessions waiting on interactive user responses (ask_question, grill-me).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

DEFAULT_HYBRID_TIMEOUT_SECONDS: float = 600.0  # 10 minutes

class WaitingMode(str, Enum):
    """Supported interactive waiting modes."""
    UNLIMITED = "unlimited"
    FIXED_TIMER = "fixed_timer"
    HYBRID = "hybrid"

@dataclass
class WaitingResult:
    """Evaluation result for an interactive user prompt state."""
    is_waiting: bool
    mode: WaitingMode
    elapsed_wait_seconds: float
    timeout_seconds: float
    is_expired: bool
    should_block_shutdown: bool
    details: str

def is_interactive_prompt_pending(session_or_step: Dict[str, Any]) -> bool:
    """
    Checks if a session evaluation or raw transcript step indicates
    an interactive user prompt is pending response.
    """
    if not isinstance(session_or_step, dict):
        return False

    status = session_or_step.get("status")
    if status == "WAITING_USER":
        return True

    # Check raw tool calls if passed a step dictionary
    tool_calls = session_or_step.get("tool_calls", [])
    for call in tool_calls:
        name = call.get("tool_name") or call.get("name") or ""
        if name == "ask_question":
            return True

    return False

def _evaluate_unlimited(elapsed: float, timeout: float) -> WaitingResult:
    """Handles Mode 1: Unlimited waiting."""
    return WaitingResult(
        is_waiting=True,
        mode=WaitingMode.UNLIMITED,
        elapsed_wait_seconds=elapsed,
        timeout_seconds=float("inf"),
        is_expired=False,
        should_block_shutdown=True,
        details=f"Unlimited waiting active: interactive question awaiting user ({elapsed:.1f}s elapsed)"
    )

def _evaluate_fixed_or_hybrid(mode: WaitingMode, elapsed: float, timeout: float) -> WaitingResult:
    """Handles Mode 2 (Fixed Timer) and Mode 3 (Hybrid grace window)."""
    is_expired = elapsed >= timeout
    should_block = not is_expired

    if is_expired:
        details = (
            f"{mode.value.capitalize()} window expired ({elapsed:.1f}s >= {timeout:.1f}s): "
            "releasing shutdown block"
        )
    else:
        details = (
            f"{mode.value.capitalize()} window active ({elapsed:.1f}s / {timeout:.1f}s): "
            "blocking shutdown"
        )

    return WaitingResult(
        is_waiting=True,
        mode=mode,
        elapsed_wait_seconds=elapsed,
        timeout_seconds=timeout,
        is_expired=is_expired,
        should_block_shutdown=should_block,
        details=details
    )

def evaluate_waiting_state(
    session_state: Dict[str, Any],
    mode: WaitingMode = WaitingMode.HYBRID,
    timeout_seconds: float = DEFAULT_HYBRID_TIMEOUT_SECONDS
) -> WaitingResult:
    """
    Evaluates whether a session's waiting state should block auto-shutdown.

    Args:
        session_state: Session evaluation dict or transcript step.
        mode: WaitingMode (UNLIMITED, FIXED_TIMER, or HYBRID).
        timeout_seconds: Max seconds to wait before expiration in TIMER or HYBRID mode.

    Returns:
        WaitingResult containing expiration and block decision.
    """
    if not is_interactive_prompt_pending(session_state):
        return WaitingResult(
            is_waiting=False,
            mode=mode,
            elapsed_wait_seconds=0.0,
            timeout_seconds=timeout_seconds,
            is_expired=False,
            should_block_shutdown=False,
            details="Session is not awaiting interactive user input"
        )

    elapsed = max(0.0, float(session_state.get("silence", 0.0)))

    if mode == WaitingMode.UNLIMITED:
        return _evaluate_unlimited(elapsed, timeout_seconds)

    return _evaluate_fixed_or_hybrid(mode, elapsed, max(0.0, timeout_seconds))
