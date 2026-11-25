# -*- coding: utf-8 -*-
"""
Smart Shutdown — Mode 0: Quick 30-Second Real Test Mode.
Forcefully closes open applications at T-10s and executes system shutdown at T-0s.
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
    setup_logger,
    acquire_single_instance_lock,
    hide_console_window,
    AntigravitySessionAnalyzer,
    CountdownWindow
)

def parse_args():
    parser = argparse.ArgumentParser(description="Mode 0: Quick 30-Second Real Test Mode")
    parser.add_argument("--countdown", type=int, default=30,
                        help="Countdown duration in seconds (default: 30s)")
    parser.add_argument("--test-shutdown-skip", action="store_true",
                        help="Forcefully close apps at T-10s but skip actual Windows shutdown at T-0")
    parser.add_argument("--idle-buffer", type=int, default=10,
                        help="Idle silence buffer in seconds (default: 10s)")
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

    if not args.no_hide:
        hide_console_window(logger=logger)

    shutdown_status = "SKIPPED" if args.test_shutdown_skip else "ACTIVE"
    logger.warning(
        f"[MODE_0_START] Quick 30s Real Test Mode (countdown: {args.countdown}s, "
        f"real app closure at T-10s, shutdown: {shutdown_status})..."
    )

    analyzer = AntigravitySessionAnalyzer(
        brain_dir=DEFAULT_BRAIN_DIR,
        start_timestamp=time.time(),
        logger=logger
    )

    app = CountdownWindow(
        countdown_seconds=args.countdown,
        dry_run=False,
        skip_shutdown=args.test_shutdown_skip,
        summary_info=f"Quick Test Mode ({args.countdown}s · Real App Close at T-10s)",
        analyzer=analyzer,
        idle_buffer=args.idle_buffer,
        logger=logger
    )
    app.mainloop()
    logger.info("[MODE_0_END] Quick test mode completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
