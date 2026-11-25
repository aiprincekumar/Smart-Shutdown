# -*- coding: utf-8 -*-
"""
core.monitor: Smart Shutdown monitor loop orchestrator.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import logging
from core.config import (
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    DEFAULT_POLL_INTERVAL
)
from core.console import hide_console_window
from core.analyzer import AntigravitySessionAnalyzer
from core.gui import CountdownWindow

def run_monitor_loop(analyzer: AntigravitySessionAnalyzer, countdown_seconds: int = DEFAULT_COUNTDOWN_SECONDS,
                     idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS, poll_interval: int = DEFAULT_POLL_INTERVAL,
                     dry_run: bool = False, wait_for_task: bool = False, hide_console: bool = True, logger=None):
    """
    Coordinates session analysis, immediately presents the interactive CountdownWindow GUI,
    and conducts monitoring until shutdown or user cancellation.
    """
    logger = logger or logging.getLogger("SmartShutdown")

    if hide_console:
        hide_console_window(logger)

    logger.info("="*70)
    logger.info(" Smart Shutdown Started")
    logger.info(f" Mode: {'SAFE TEST / DRY-RUN (No shutdown)' if dry_run else 'PRODUCTION (System will shut down)'}")
    logger.info(f" Countdown: {countdown_seconds}s | Idle Buffer: {idle_buffer}s | Poll: {poll_interval}s")
    logger.info(f" Brain Directory: {analyzer.brain_dir}")
    logger.info("="*70)

    # Immediate GUI Presentation: NEVER wait in an invisible background sleep loop!
    # Launch CountdownWindow INSTANTLY on user screen (<0.5s).
    logger.info(f"[LAUNCHING_GUI_IMMEDIATELY] Opening always-on-top {countdown_seconds}s countdown GUI window instantly...")

    app = CountdownWindow(
        countdown_seconds=countdown_seconds,
        dry_run=dry_run,
        summary_info="Initializing live task monitor...",
        analyzer=analyzer,
        idle_buffer=idle_buffer,
        logger=logger
    )
    app.mainloop()

    if app.cancelled:
        logger.info("[SENTINEL] Execution finished: User cancelled shutdown. Standby ended.")
    else:
        logger.info("[SENTINEL] Shutdown workflow concluded.")
