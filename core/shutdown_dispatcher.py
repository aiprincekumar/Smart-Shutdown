# -*- coding: utf-8 -*-
"""
core.shutdown_dispatcher: Windows power action execution and abort dispatcher.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import ctypes
import logging
import subprocess
from typing import List, Optional
from core.config import log_telemetry_event

logger_instance = logging.getLogger("SmartShutdown")

_POWER_ACTION_MAP = {
    "shutdown": "Shutdown",
    "hibernate": "Hibernate",
    "sleep": "Sleep",
    "lock screen": "Lock Screen",
}


def _run_cmd(cmd: List[str], log: logging.Logger, label: str) -> bool:
    """Execute a system power subprocess command safely and log exit status."""
    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        log.info(f"[SHUTDOWN_DISPATCH] {label} command exit code: {res.returncode}")
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"[SHUTDOWN_DISPATCH_ERROR] {label} failed (code {e.returncode}): {e.stderr}")
        return False
    except Exception as e:
        log.error(f"[SHUTDOWN_DISPATCH_ERROR] Unexpected {label} error: {e}")
        return False


def _dispatch_suspend(hibernate: bool, log: logging.Logger) -> bool:
    """Dispatch Windows Hibernate or Sleep with Win32 / rundll32 fallback."""
    if hibernate:
        if _run_cmd(["shutdown.exe", "/h"], log, "Hibernate"):
            return True
        try:
            return bool(ctypes.windll.powrprof.SetSuspendState(1, 0, 0))
        except Exception as e:
            log.error(f"[SHUTDOWN_DISPATCH_ERROR] Hibernate SetSuspendState failed: {e}")
            return False

    try:
        if ctypes.windll.powrprof.SetSuspendState(0, 0, 0):
            return True
    except Exception as e:
        log.warning(f"[SHUTDOWN_DISPATCH] SetSuspendState sleep failed ({e}), trying rundll32 fallback.")
    return _run_cmd(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], log, "Sleep")


def _dispatch_lock(log: logging.Logger) -> bool:
    """Dispatch Windows workstation lock via user32 with rundll32 fallback."""
    try:
        if ctypes.windll.user32.LockWorkStation():
            return True
    except Exception as e:
        log.warning(f"[SHUTDOWN_DISPATCH] LockWorkStation failed ({e}), trying rundll32 fallback.")
    return _run_cmd(["rundll32.exe", "user32.dll,LockWorkStation"], log, "Lock Screen")


def _dispatch_power_action(action: str, delay: int, log: logging.Logger) -> bool:
    """Route normalized target action to the corresponding OS power routine."""
    if action == "Hibernate":
        log.critical("[SHUTDOWN_DISPATCH] Executing: shutdown.exe /h (Hibernate)")
        log_telemetry_event(log, "SHUTDOWN_DISPATCH_EXECUTED", {"action": action, "command": ["shutdown.exe", "/h"]})
        return _dispatch_suspend(hibernate=True, log=log)

    if action == "Sleep":
        log.critical("[SHUTDOWN_DISPATCH] Executing: SetSuspendState(0, 0, 0) (Sleep)")
        log_telemetry_event(log, "SHUTDOWN_DISPATCH_EXECUTED", {"action": action, "command": ["SetSuspendState", "0,0,0"]})
        return _dispatch_suspend(hibernate=False, log=log)

    if action == "Lock Screen":
        log.critical("[SHUTDOWN_DISPATCH] Executing: LockWorkStation (Lock Screen)")
        log_telemetry_event(log, "SHUTDOWN_DISPATCH_EXECUTED", {"action": action, "command": ["LockWorkStation"]})
        return _dispatch_lock(log=log)

    cmd = ["shutdown.exe", "/s", "/t", str(delay)]
    log.critical(f"[SHUTDOWN_DISPATCH] Executing: {' '.join(cmd)}")
    log_telemetry_event(log, "SHUTDOWN_DISPATCH_EXECUTED", {"action": "Shutdown", "command": cmd})
    return _run_cmd(cmd, log, "Shutdown")


def execute_shutdown(
    dry_run: bool = False,
    delay_seconds: int = 0,
    logger: Optional[logging.Logger] = None,
    target_action: str = "Shutdown",
) -> bool:
    """Execute Windows power action or simulate execution in dry-run mode."""
    log = logger or logger_instance
    delay = max(0, int(delay_seconds))
    raw_action = (target_action or "Shutdown").strip()
    action = _POWER_ACTION_MAP.get(raw_action.lower(), "Shutdown")

    if dry_run:
        log.warning(f"[SAFE DRY RUN] Windows {action} simulated (delay={delay}s)")
        log_telemetry_event(log, "SHUTDOWN_DISPATCH_SIMULATED", {"action": action, "delay": delay})
        return True

    return _dispatch_power_action(action, delay, log)


def abort_shutdown(
    dry_run: bool = False,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Aborts a pending Windows shutdown using 'shutdown.exe /a'."""
    log = logger or logger_instance

    if dry_run:
        log.info("[SAFE DRY RUN] Windows shutdown abort simulated: 'shutdown.exe /a'")
        log_telemetry_event(log, "SHUTDOWN_ABORT_SIMULATED", {})
        return True

    cmd = ["shutdown.exe", "/a"]
    log.info(f"[SHUTDOWN_DISPATCH] Aborting pending shutdown: {' '.join(cmd)}")
    log_telemetry_event(log, "SHUTDOWN_ABORT_EXECUTED", {"command": cmd})

    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        log.info(f"[SHUTDOWN_DISPATCH] Abort command succeeded (code {res.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        log.warning(f"[SHUTDOWN_ABORT_INFO] Abort completed (info: {e.stderr.strip()})")
        return True
    except Exception as e:
        log.error(f"[SHUTDOWN_ABORT_ERROR] Unexpected error aborting shutdown: {e}")
        return False
