# -*- coding: utf-8 -*-
"""
Smart Shutdown — Mode 4: Immediate GUI Preview Test.
Immediately opens the Tkinter countdown window in safe simulation mode to preview UI, animations, and sound chimes.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import (
    DEFAULT_LOG_FILE,
    setup_logger,
    acquire_single_instance_lock,
    hide_console_window,
    CountdownWindow
)

def parse_args():
    parser = argparse.ArgumentParser(description="Mode 4: Immediate GUI Preview Test (20s Countdown)")
    parser.add_argument("--countdown", type=int, default=20,
                        help="Countdown duration in seconds (default: 20s)")
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

    logger.info(f"[MODE_4_START] Immediate GUI preview test started ({args.countdown}s countdown, dry_run: True)...")

    app = CountdownWindow(
        countdown_seconds=args.countdown,
        dry_run=True,
        summary_info=f"Direct GUI Preview Test ({args.countdown}s Countdown)",
        analyzer=None,  # Pure preview: countdown ticks down unconditionally
        logger=logger
    )
    app.mainloop()
    logger.info("[MODE_4_END] GUI preview test closed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
