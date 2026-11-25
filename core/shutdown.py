# -*- coding: utf-8 -*-
"""
core.shutdown: Windows shutdown execution engine (graceful OS shutdown & dry-run simulation).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import subprocess
import logging
from core.config import log_telemetry_event

def execute_system_shutdown(dry_run: bool = False, skip_shutdown: bool = False, logger=None) -> bool:
    """
    Triggers Windows system shutdown or simulates it in dry-run mode.
    Gracefully allows OS applications to terminate.
    """
    logger = logger or logging.getLogger("SmartShutdown")
    if dry_run or skip_shutdown:
        if skip_shutdown:
            msg = "[TEST_SHUTDOWN_SKIP] Real app force-close completed. Windows shutdown skipped per --test-shutdown-skip."
        else:
            msg = "[SAFE TEST / DRY RUN] Simulating shutdown: In production, 'shutdown.exe /s /t 0' would execute now."
        logger.warning(msg)
        print("\n" + "="*72)
        print(f"  {msg}")
        print("  PC will NOT shut down. Safe test verification successful!")
        print("="*72 + "\n")
        log_telemetry_event(logger, "SHUTDOWN_SIMULATED", {"dry_run": dry_run, "skip_shutdown": skip_shutdown})
        return True

    msg = "[CRITICAL] Initiating Windows shutdown via 'shutdown.exe /s /t 0'..."
    logger.critical(msg)
    log_telemetry_event(logger, "SHUTDOWN_TRIGGERED", {"command": "shutdown.exe /s /t 0"})
    print("\n" + "!"*72)
    print(f"  {msg}")
    print("!"*72 + "\n")
    try:
        subprocess.run(["shutdown.exe", "/s", "/t", "0"], check=True)
        return True
    except Exception as e:
        err = f"[ERROR] Failed to execute shutdown command: {e}"
        logger.error(err)
        print(err)
        return False
