# -*- coding: utf-8 -*-
"""
preview_countdown_overlay: Standalone Preview Runner for Smart Shutdown Floating Countdown Overlay.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import argparse
import tkinter as tk
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from gui.countdown_overlay import CountdownOverlay


def parse_args():
    parser = argparse.ArgumentParser(description="Preview Smart Shutdown Countdown Overlay (20s Preview)")
    parser.add_argument("--countdown", type=int, default=20,
                        help="Countdown duration in seconds (default: 20s)")
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"[PREVIEW_OVERLAY] Launching Countdown Overlay preview ({args.countdown}s)...")
    root = tk.Tk()
    root.withdraw()
    overlay = CountdownOverlay(
        parent=root,
        countdown_seconds=args.countdown,
        on_cancel=lambda: print("[PREVIEW_OVERLAY] Countdown cancelled by user."),
        on_timeout=lambda: print("[PREVIEW_OVERLAY] Countdown expired (simulated shutdown trigger)."),
        on_reset=lambda: print("[PREVIEW_OVERLAY] Physical activity detected, timer reset."),
    )
    root.mainloop()
    print("[PREVIEW_OVERLAY] Countdown overlay closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
