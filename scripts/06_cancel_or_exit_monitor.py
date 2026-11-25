# -*- coding: utf-8 -*-
"""
Smart Shutdown — Mode 6: Cancel / Abort Auto-Shutdown and Exit Monitor.
Cancels active Windows system shutdown timers (shutdown /a) and terminates running background monitor instances.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import (
    LOCK_FILE,
    DEFAULT_LOG_FILE,
    setup_logger,
    get_ancestor_process_ids
)

def parse_args():
    parser = argparse.ArgumentParser(description="Mode 6: Cancel / Abort Auto-Shutdown and Exit Monitor")
    parser.add_argument("--force", action="store_true",
                        help="Force kill background monitor without interactive prompt")
    parser.add_argument("--log-file", type=str, default=str(DEFAULT_LOG_FILE),
                        help="Path to log file")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug logging")
    return parser.parse_args()

def _cleanup_lock_file(lock_path: Path, label: str, force: bool, logger) -> bool:
    """Inspect a lock file, optionally terminate its PID, and unlink it. Returns True if found."""
    if not lock_path.exists():
        return False
    try:
        pid_text = lock_path.read_text(encoding="utf-8").strip()
        if pid_text.isdigit():
            target_pid = int(pid_text)
            my_pid = os.getpid()
            ancestor_pids = get_ancestor_process_ids(my_pid)

            if target_pid != my_pid and target_pid > 4 and target_pid not in ancestor_pids:
                print(f"  ℹ️ Detected running Smart Shutdown monitor process with PID {target_pid} ({label}).")
                should_kill = force
                if not should_kill:
                    try:
                        ans = input(f"  Terminate the background monitor process [PID {target_pid}]? (Y/n): ").strip().lower()
                        should_kill = ans in ("", "y", "yes")
                    except EOFError:
                        should_kill = True

                if should_kill:
                    try:
                        res = subprocess.run(
                            ["taskkill", "/F", "/PID", str(target_pid)],
                            capture_output=True,
                            text=True
                        )
                        if res.returncode == 0:
                            print(f"  ✅ [SUCCESS] Background monitor PID {target_pid} terminated.")
                            logger.info(f"[CANCEL_MONITOR] Terminated monitor PID {target_pid}")
                        else:
                            print(f"  ℹ️ Process {target_pid} already exited.")
                    except Exception as e:
                        logger.error(f"Failed to terminate PID {target_pid}: {e}")
                else:
                    print(f"  ℹ️ Background monitor process PID {target_pid} left running.")

        lock_path.unlink(missing_ok=True)
        print(f"  ✅ [SUCCESS] Cleaned up {label}.")
    except Exception as e:
        logger.error(f"Error handling lock file {lock_path}: {e}")
    return True


def main():
    args = parse_args()
    logger = setup_logger(Path(args.log_file), debug=args.debug)

    print("\n" + "="*72)
    print("    Smart Shutdown: Option 6 - Exit / Abort Active Shutdown")
    print("    Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)")
    print("="*72 + "\n")

    # 1. Cancel active Windows system shutdown timer
    try:
        res = subprocess.run(["shutdown.exe", "/a"], capture_output=True, text=True)
        if res.returncode == 0:
            msg = "[SUCCESS] Active Windows system shutdown has been CANCELLED [shutdown /a]."
            logger.info(msg)
            print(f"  ✅ {msg}")
        else:
            msg = "[INFO] No Windows system shutdown command was pending."
            logger.info(msg)
            print(f"  ℹ️ {msg}")
    except Exception as e:
        logger.error(f"[ERROR] Could not invoke shutdown /a: {e}")
        print(f"  ❌ Error executing shutdown /a: {e}")

    # 2. Check for running monitor lock files (active + legacy) and active process
    legacy_lock_file = ROOT_DIR / "auto_shutdown.lock"
    cleaned_primary = _cleanup_lock_file(LOCK_FILE, LOCK_FILE.name, args.force, logger)
    cleaned_legacy = _cleanup_lock_file(legacy_lock_file, f"legacy {legacy_lock_file.name}", args.force, logger)
    if not cleaned_primary and not cleaned_legacy:
        print("  ℹ️ No background monitor lock file found.")

    print("\n" + "="*72)
    print("  Smart Shutdown Exit / Cancellation Complete.")
    print("="*72 + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
