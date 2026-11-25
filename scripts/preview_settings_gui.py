# -*- coding: utf-8 -*-
"""
preview_settings_gui: Standalone Preview Runner for Smart Shutdown Settings GUI.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from gui.settings_window import SettingsWindow, SettingsConfig


def parse_args():
    parser = argparse.ArgumentParser(description="Preview Smart Shutdown Settings GUI")
    parser.add_argument("--waiting-mode", type=str, default="Hybrid", choices=["Unlimited", "Timer", "Hybrid"],
                        help="Default waiting mode (default: Hybrid)")
    return parser.parse_args()


def main():
    args = parse_args()
    print("[PREVIEW_SETTINGS] Launching Smart Shutdown Settings GUI...")
    config = SettingsConfig(waiting_mode=args.waiting_mode)
    app = SettingsWindow(config=config)
    app.mainloop()
    print("[PREVIEW_SETTINGS] Settings GUI closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
