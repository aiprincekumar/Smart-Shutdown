# -*- coding: utf-8 -*-
"""
Mode 7: Toggle Windows Auto-Startup on Boot.
Enables, disables, or inspects the Windows Startup folder shortcut for Smart Shutdown.
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
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    setup_logger,
    enable_startup,
    disable_startup,
    toggle_startup,
    show_startup_status
)


def parse_args():
    parser = argparse.ArgumentParser(description="Mode 7: Toggle Windows Auto-Startup on Boot (Smart Shutdown Mini-HUD)")
    parser.add_argument("--countdown", type=int, default=DEFAULT_COUNTDOWN_SECONDS,
                        help=f"Countdown duration in seconds (default: {DEFAULT_COUNTDOWN_SECONDS}s)")
    parser.add_argument("--idle-buffer", type=int, default=DEFAULT_IDLE_BUFFER_SECONDS,
                        help=f"Idle silence buffer in seconds (default: {DEFAULT_IDLE_BUFFER_SECONDS}s)")
    parser.add_argument("--status", action="store_true",
                        help="Display current startup configuration status")
    parser.add_argument("--enable", action="store_true",
                        help="Enable Windows auto-startup shortcut in Mini-HUD mode")
    parser.add_argument("--disable", action="store_true",
                        help="Disable and remove Windows auto-startup shortcut")
    parser.add_argument("--toggle", action="store_true",
                        help="Toggle Windows auto-startup on/off (default)")
    parser.add_argument("--no-mini-hud", action="store_true",
                        help="Launch full GUI cockpit instead of mini-hud on boot")
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
    mini_hud = not args.no_mini_hud

    if args.status:
        show_startup_status(logger=logger)
        return 0

    if args.enable:
        success = enable_startup(countdown=args.countdown, idle_buffer=args.idle_buffer, mini_hud=mini_hud, logger=logger)
        return 0 if success else 1

    if args.disable:
        success = disable_startup(logger=logger)
        return 0 if success else 1

    # Default action: toggle
    success = toggle_startup(countdown=args.countdown, idle_buffer=args.idle_buffer, mini_hud=mini_hud, logger=logger)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
