# -*- coding: utf-8 -*-
"""
Smart Shutdown — Mode 5: Single Detection Status Check.
Inspects Antigravity brain sessions once, outputs a structured terminal report, and exits without countdown.
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
    DEFAULT_IDLE_BUFFER_SECONDS,
    DEFAULT_WINDOW_HOURS,
    DEFAULT_LOG_FILE,
    setup_logger,
    AntigravitySessionAnalyzer
)

def parse_args():
    parser = argparse.ArgumentParser(description="Mode 5: Single Detection Status Check")
    parser.add_argument("--idle-buffer", type=int, default=DEFAULT_IDLE_BUFFER_SECONDS,
                        help=f"Idle silence buffer in seconds (default: {DEFAULT_IDLE_BUFFER_SECONDS}s)")
    parser.add_argument("--window-hours", type=float, default=DEFAULT_WINDOW_HOURS,
                        help=f"Hours window to inspect active sessions (default: {DEFAULT_WINDOW_HOURS}h)")
    parser.add_argument("--since-start", action="store_true",
                        help="Only inspect sessions modified since this check was started")
    parser.add_argument("--log-file", type=str, default=str(DEFAULT_LOG_FILE),
                        help="Path to log file")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug logging")
    parser.add_argument("--no-hide", action="store_true",
                        help="Keep the console window visible (default behavior)")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = setup_logger(Path(args.log_file), debug=args.debug)

    logger.info("[MODE_5_START] Inspecting Antigravity sessions once...")

    analyzer = AntigravitySessionAnalyzer(
        brain_dir=DEFAULT_BRAIN_DIR,
        window_hours=args.window_hours,
        start_timestamp=time.time(),
        filter_since_start=args.since_start,
        logger=logger
    )

    res = analyzer.evaluate_all(idle_buffer=args.idle_buffer)

    print("\n" + "="*70)
    print(" SMART SHUTDOWN — ANTIGRAVITY SESSION REPORT")
    print("="*70)
    print(f" All Tasks Complete: {'YES ✅' if res['all_completed'] else 'NO ⏳'}")
    print(f" Summary: {res['summary']}")
    print(f" Idle Buffer Required: {args.idle_buffer}s")
    print(f" Monitored Sessions Count: {len(res.get('sessions', []))}")
    print("-"*70)
    for s in res.get('sessions', [])[:10]:
        cid = s.get('conversation_id', 'unknown')[:8]
        st = s.get('status', 'UNKNOWN')
        sil = s.get('silence', 0)
        rea = s.get('reason', '')
        print(f"  [{st:12}] {cid}... | silence={sil:5.1f}s | {rea}")
    print("="*70 + "\n")

    return 0 if res["all_completed"] else 1

if __name__ == "__main__":
    sys.exit(main())
