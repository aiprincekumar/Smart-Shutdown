# -*- coding: utf-8 -*-
"""
Smart Shutdown — Mode 2: Production Monitor - 10-Minute Countdown.
Monitors Antigravity sessions, auto-pauses/resumes, and executes system shutdown after 10 minutes idle.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import argparse
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import (
    DEFAULT_BRAIN_DIR,
    DEFAULT_LOG_FILE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_WINDOW_HOURS,
    setup_logger,
    acquire_single_instance_lock,
    AntigravitySessionAnalyzer,
    run_monitor_loop
)

def parse_args():
    parser = argparse.ArgumentParser(description="Mode 2: Production Monitor - 10-Minute Countdown (600s)")
    parser.add_argument("--countdown", type=int, default=600,
                        help="Countdown duration in seconds (default: 600s / 10 minutes)")
    parser.add_argument("--idle-buffer", type=int, default=60,
                        help="Idle silence buffer in seconds (default: 60s)")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                        help=f"Polling interval in seconds (default: {DEFAULT_POLL_INTERVAL}s)")
    parser.add_argument("--window-hours", type=float, default=DEFAULT_WINDOW_HOURS,
                        help=f"Hours window to inspect active sessions (default: {DEFAULT_WINDOW_HOURS}h)")
    parser.add_argument("--since-start", action="store_true",
                        help="Only inspect sessions modified since this script was started")
    parser.add_argument("--wait-for-task", action="store_true",
                        help="Wait until at least one task starts before arming completion trigger")
    parser.add_argument("--log-file", type=str, default=str(DEFAULT_LOG_FILE),
                        help="Path to log file")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug logging")
    parser.add_argument("--no-hide", action="store_true",
                        help="Keep the console window visible")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = setup_logger(Path(args.log_file), debug=args.debug)
    acquire_single_instance_lock(logger=logger)

    analyzer = AntigravitySessionAnalyzer(
        brain_dir=DEFAULT_BRAIN_DIR,
        window_hours=args.window_hours,
        start_timestamp=time.time(),
        filter_since_start=args.since_start,
        logger=logger
    )

    run_monitor_loop(
        analyzer=analyzer,
        countdown_seconds=args.countdown,
        idle_buffer=args.idle_buffer,
        poll_interval=args.poll_interval,
        dry_run=False,
        wait_for_task=args.wait_for_task,
        hide_console=(not args.no_hide),
        logger=logger
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
