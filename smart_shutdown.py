# -*- coding: utf-8 -*-
"""
Smart Shutdown Engine (Dispatcher & Unified CLI).
Department 13 (SRE & Backup) & Department 14 (Telemetry & Observability) Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

This lightweight root module delegates all business logic to the modular `core/` package
and provides a unified CLI interface with single-GUI default launcher.
"""

import sys
import time
import argparse
from typing import Optional, List
from pathlib import Path

from core import (
    DEFAULT_BRAIN_DIR,
    DEFAULT_LOG_FILE,
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_WINDOW_HOURS,
    setup_logger,
    acquire_single_instance_lock,
    hide_console_window,
    force_close_all_apps,
    AntigravitySessionAnalyzer,
    CountdownWindow,
    show_startup_status,
    enable_startup,
    disable_startup,
    toggle_startup,
    run_monitor_loop,
    load_settings_config,
)
from gui import launch_unified_gui


def _add_mode_arguments(parser: argparse.ArgumentParser) -> None:
    """Register GUI, headless, and test/live execution mode CLI arguments."""
    parser.add_argument("--gui", action="store_true", help="Launch the Single Unified GUI Desktop Application (Default)")
    parser.add_argument("--mini-hud", "--mini", "--hud", action="store_true", dest="mini_hud", help="Launch directly in compact Topmost Mini HUD overlay mode on Windows startup")
    parser.add_argument("--no-mini-hud", "--full-gui", action="store_true", dest="no_mini_hud", help="Launch directly into the full desktop cockpit window instead of Mini HUD")
    parser.add_argument("--headless", action="store_true", help="Run in headless background monitoring mode without spawning a GUI window")
    parser.add_argument("--countdown", type=int, default=DEFAULT_COUNTDOWN_SECONDS, help=f"Countdown duration in seconds (default: {DEFAULT_COUNTDOWN_SECONDS}s)")
    parser.add_argument("--idle-buffer", type=int, default=DEFAULT_IDLE_BUFFER_SECONDS, help=f"Idle silence buffer in seconds (default: {DEFAULT_IDLE_BUFFER_SECONDS}s)")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL, help=f"Polling interval in seconds (default: {DEFAULT_POLL_INTERVAL}s)")
    parser.add_argument("--window-hours", type=float, default=DEFAULT_WINDOW_HOURS, help=f"Hours window to inspect active sessions (default: {DEFAULT_WINDOW_HOURS}h)")
    parser.add_argument("--dry-run", "--test", action="store_true", dest="dry_run", help="Safe testing mode: countdown and audio alert work, but PC will NOT shut down and apps will NOT close")
    parser.add_argument("--force-close", action="store_true", help="Directly launch countdown in LIVE mode: forcefully closes apps at T-10s and shuts down PC at T-0")
    parser.add_argument("--test-shutdown-skip", action="store_true", help="In live mode, forcefully close apps at T-10s but skip actual Windows shutdown at T-0")
    parser.add_argument("--test-gui", action="store_true", help="Directly open the Tkinter countdown window immediately in safe simulation mode")


def _add_utility_arguments(parser: argparse.ArgumentParser) -> None:
    """Register diagnostic, logging, and Windows startup management arguments."""
    parser.add_argument("--check-once", action="store_true", help="Inspect sessions once, output detailed status report, and exit")
    parser.add_argument("--since-start", action="store_true", help="Only inspect sessions modified since this script was started")
    parser.add_argument("--wait-for-task", action="store_true", help="Wait until at least one task starts before arming completion trigger")
    parser.add_argument("--log-file", type=str, default=str(DEFAULT_LOG_FILE), help="Path to log file (default: logs/smart_shutdown.log)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--no-hide", action="store_true", help="Keep the Windows command prompt console visible (do not hide with SW_HIDE)")
    parser.add_argument("--force-close-test", action="store_true", help="Simulate and print all processes targeted for termination at T-10s without killing them")
    parser.add_argument("--startup-status", action="store_true", help="Check whether Auto-Startup is enabled or disabled in Windows Startup")
    parser.add_argument("--enable-startup", action="store_true", help="Enable Auto-Startup by creating shortcut in Windows Startup folder")
    parser.add_argument("--disable-startup", action="store_true", help="Disable Auto-Startup by removing shortcut from Windows Startup folder")
    parser.add_argument("--toggle-startup", action="store_true", help="Toggle Windows Auto-Startup state between enabled and disabled")


def _build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser with examples and grouped flags."""
    parser = argparse.ArgumentParser(
        description="Smart Shutdown (Unified Cockpit & Dispatcher)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smart_shutdown.py
  python smart_shutdown.py --gui
  python smart_shutdown.py --headless --countdown 300
  python smart_shutdown.py --countdown 30 --force-close
  python smart_shutdown.py --test --countdown 30
  python smart_shutdown.py --check-once --no-hide
        """,
    )
    _add_mode_arguments(parser)
    _add_utility_arguments(parser)
    return parser


def parse_arguments(argv: Optional[List[str]] = None):
    """Parse CLI arguments while preserving standard default values for parity."""
    return _build_parser().parse_args(argv)


def handle_startup_commands(args, logger) -> Optional[int]:
    """Process Windows startup commands if specified."""
    if args.startup_status:
        show_startup_status(logger=logger)
        return 0
    if args.enable_startup:
        return 0 if enable_startup(countdown=args.countdown, idle_buffer=args.idle_buffer, mini_hud=True, logger=logger) else 1
    if args.disable_startup:
        return 0 if disable_startup(logger=logger) else 1
    if args.toggle_startup:
        return 0 if toggle_startup(countdown=args.countdown, idle_buffer=args.idle_buffer, mini_hud=True, logger=logger) else 1
    return None


def _has_cli_flag(flag: str, argv: Optional[List[str]] = None) -> bool:
    """Return True if an explicit CLI flag was supplied on the command line."""
    tokens = sys.argv[1:] if argv is None else argv
    prefix = f"{flag}="
    return any(tok == flag or tok.startswith(prefix) for tok in tokens)


def _dispatch_combined_gui(args, logger) -> int:
    """Launch UnifiedSentinelApp using persisted settings plus explicit CLI overrides."""
    logger.info("[LAUNCHER] Initializing Single Unified Sentinel Desktop GUI...")
    cfg = load_settings_config()
    if _has_cli_flag("--countdown"):
        if args.dry_run or getattr(cfg, "execution_mode", "Live") == "Simulation":
            cfg.simulation_timer_sec = args.countdown
        else:
            cfg.master_shutdown_timer_min = max(1, args.countdown // 60)
    if _has_cli_flag("--idle-buffer"):
        cfg.user_inactivity_sec = args.idle_buffer
    cfg.clamp()
    if args.mini_hud:
        start_hud = True
    elif getattr(args, "no_mini_hud", False):
        start_hud = False
    else:
        start_hud = bool(getattr(cfg, "mini_hud_on_startup", True))
    launch_unified_gui(config=cfg, dry_run=args.dry_run, start_in_mini_hud=start_hud, logger=logger)
    return 0


def _print_check_once_report(res: dict, idle_buffer: int) -> None:
    """Print formatted session inspection summary for --check-once mode."""
    print("\n" + "=" * 70)
    print(" SMART SHUTDOWN — ANTIGRAVITY SESSION REPORT")
    print("=" * 70)
    print(f" All Tasks Complete: {'YES ✅' if res['all_completed'] else 'NO ⏳'}")
    print(f" Summary: {res['summary']}")
    print(f" Idle Buffer Required: {idle_buffer}s")
    print(f" Monitored Sessions Count: {len(res.get('sessions', []))}")
    print("-" * 70)
    for s in res.get("sessions", [])[:10]:
        print(f"  [{s.get('status', 'UNKNOWN'):12}] {s.get('conversation_id', 'unknown')[:8]}... | silence={s.get('silence', 0):5.1f}s | {s.get('reason', '')}")
    print("=" * 70 + "\n")


def _dispatch_cli_modes(args, logger, start_time: float) -> int:
    """Execute legacy headless, force-close, test-gui, and check-once CLI modes."""
    analyzer = AntigravitySessionAnalyzer(
        brain_dir=DEFAULT_BRAIN_DIR, window_hours=args.window_hours,
        start_timestamp=start_time, filter_since_start=args.since_start, logger=logger,
    )
    if args.force_close:
        status = "SKIPPED" if args.test_shutdown_skip else "ACTIVE"
        logger.warning(f"[FORCE_CLOSE_LIVE] Launching direct LIVE countdown (countdown: {args.countdown}s, real app closure at T-10s, shutdown: {status})...")
        CountdownWindow(
            countdown_seconds=args.countdown, dry_run=False, skip_shutdown=args.test_shutdown_skip,
            summary_info=f"Quick Test Mode ({args.countdown}s · Real App Close at T-10s)",
            analyzer=analyzer, idle_buffer=args.idle_buffer, logger=logger,
        ).mainloop()
        logger.info("[FORCE_CLOSE_LIVE] Force-close live countdown session closed.")
        return 0
    if args.test_gui:
        logger.info(f"[TEST_GUI] Launching direct GUI test (countdown: {args.countdown}s, dry_run: True)...")
        CountdownWindow(
            countdown_seconds=args.countdown, dry_run=True,
            summary_info=f"Direct GUI Preview Test ({args.countdown}s Countdown)",
            analyzer=None, idle_buffer=args.idle_buffer, logger=logger,
        ).mainloop()
        logger.info("[TEST_GUI] GUI preview test closed.")
        return 0
    if args.check_once:
        logger.info("[CHECK_ONCE] Performing single inspection of Antigravity sessions...")
        res = analyzer.evaluate_all(idle_buffer=args.idle_buffer)
        _print_check_once_report(res, args.idle_buffer)
        return 0 if res["all_completed"] else 1
    run_monitor_loop(
        analyzer=analyzer, countdown_seconds=args.countdown, idle_buffer=args.idle_buffer,
        poll_interval=args.poll_interval, dry_run=args.dry_run, wait_for_task=args.wait_for_task,
        hide_console=(not args.no_hide), logger=logger,
    )
    return 0


def main() -> int:
    """CLI entrypoint routing startup utilities, Combined GUI, and legacy CLI modes."""
    args = parse_arguments()
    logger = setup_logger(Path(args.log_file), debug=args.debug)
    start_time = time.time()

    startup_ret = handle_startup_commands(args, logger)
    if startup_ret is not None:
        return startup_ret
    if args.force_close_test:
        logger.info("[FORCE_CLOSE_TEST] Diagnostic check of processes targeted at T-10s...")
        force_close_all_apps(dry_run=True, logger=logger)
        return 0

    acquire_single_instance_lock(logger=logger)
    if not args.check_once and not args.no_hide:
        hide_console_window(logger=logger)

    is_explicit_cli = args.headless or args.check_once or args.force_close or args.test_gui
    if args.gui or args.mini_hud or not is_explicit_cli:
        return _dispatch_combined_gui(args, logger)
    return _dispatch_cli_modes(args, logger, start_time)


if __name__ == "__main__":
    sys.exit(main())
