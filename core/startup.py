# -*- coding: utf-8 -*-
"""
core.startup: Windows Auto-Startup Manager (Shortcut creation in Startup folder).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Any, Callable, List, Optional
from core.config import (
    WORKSPACE_DIR,
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    is_compiled_runtime,
    log_telemetry_event
)


STARTUP_SHORTCUT_NAME = "Smart_Shutdown.lnk"
LEGACY_STARTUP_SHORTCUT_NAME = "Antigravity_Auto_Shutdown.lnk"


def _get_startup_dir() -> Path:
    """Returns path to the Windows Startup folder."""
    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_startup_shortcut_path() -> Path:
    """Returns path to the shortcut inside Windows Startup folder."""
    return _get_startup_dir() / STARTUP_SHORTCUT_NAME


def is_startup_enabled() -> bool:
    """Checks whether the Auto-Shutdown shortcut exists in Windows Startup."""
    return get_startup_shortcut_path().exists()


def _has_cli_int_arg(tokens: List[str], flag: str, expected: int) -> bool:
    """Return True if tokenized CLI args include `flag <expected>` or `flag=<expected>`."""
    target = str(int(expected))
    if f"{flag}={target}" in tokens:
        return True
    return any(
        tokens[i] == flag and tokens[i + 1] == target
        for i in range(len(tokens) - 1)
    )


def startup_matches_settings(countdown: int, idle_buffer: int, mini_hud: bool) -> bool:
    """Return True if existing Smart_Shutdown.lnk already matches target CLI arguments."""
    lnk_path = get_startup_shortcut_path()
    if not lnk_path.exists():
        return False
    try:
        ps_cmd = f"$w = New-Object -ComObject WScript.Shell; $s = $w.CreateShortcut('{str(lnk_path)}'); Write-Output $s.Arguments"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        if res.returncode != 0:
            return False
        tokens = res.stdout.strip().split()
        has_hud = "--mini-hud" in tokens
        return (
            (has_hud == bool(mini_hud))
            and _has_cli_int_arg(tokens, "--countdown", countdown)
            and _has_cli_int_arg(tokens, "--idle-buffer", idle_buffer)
        )
    except Exception:
        return False


def _is_compiled() -> bool:
    """Return True when running from a frozen or Nuitka-compiled executable."""
    return is_compiled_runtime() or ("__compiled__" in globals())


def resolve_python_executable() -> str:
    """Returns sys.executable when compiled; otherwise prefers pythonw.exe to prevent console flashing."""
    if _is_compiled():
        return sys.executable
    try:
        current_exe = Path(sys.executable)
        pythonw = current_exe.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    except Exception:
        pass
    return sys.executable


def _build_startup_ps_script(lnk_path: Path, py_exe: str, arguments: str) -> str:
    """Build PowerShell script for creating the Windows Startup .lnk shortcut."""
    compiled = _is_compiled()
    working_dir = str(Path(sys.executable).resolve().parent) if compiled else str(WORKSPACE_DIR)
    icon_location = f"{sys.executable},0" if compiled else "shell32.dll,27"
    return f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{str(lnk_path)}')
$Shortcut.TargetPath = '{py_exe}'
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.IconLocation = '{icon_location}'
$Shortcut.Description = 'Smart Shutdown (Mini HUD)'
$Shortcut.WindowStyle = 7
$Shortcut.Save()
"""


def _log_startup_enabled(lnk_path: Path, py_exe: str, arguments: str, logger: logging.Logger) -> None:
    """Log and print summary after enabling Windows Auto-Startup shortcut."""
    logger.info(f"[STARTUP] Windows Auto-Startup successfully ENABLED. Shortcut: {lnk_path}")
    print("\n" + "=" * 72)
    print("  ✅ WINDOWS AUTO-STARTUP SUCCESSFULLY ENABLED")
    print("=" * 72)
    print(f"  Shortcut Location : {lnk_path}")
    print(f"  Target Executable : {py_exe}")
    print(f"  Arguments         : {arguments}")
    print("  Startup Behavior  : Runs silently in compact Topmost Mini HUD mode on boot,")
    print("                      monitoring user inactivity and Antigravity tasks autonomously.")
    print("=" * 72 + "\n")
    log_telemetry_event(logger, "STARTUP_ENABLED", {"shortcut": str(lnk_path), "target": py_exe, "arguments": arguments})


def _unlink_legacy_shortcut(startup_dir: Path, logger: logging.Logger) -> None:
    """Remove legacy startup shortcut if present after new shortcut creation."""
    legacy_path = startup_dir / LEGACY_STARTUP_SHORTCUT_NAME
    if legacy_path.exists():
        try:
            legacy_path.unlink(missing_ok=True)
            logger.info(f"[STARTUP] Migrated legacy startup shortcut: removed {legacy_path}")
        except OSError as exc:
            logger.warning(f"[STARTUP] Failed to remove legacy shortcut {legacy_path}: {exc}")


def enable_startup(
    countdown: int = DEFAULT_COUNTDOWN_SECONDS,
    idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS,
    target_script: Path = None,
    mini_hud: bool = True,
    logger=None,
) -> bool:
    """Creates a Windows Startup shortcut to autonomously run Smart Shutdown on boot in Mini-HUD mode."""
    logger = logger or logging.getLogger("SmartShutdown")
    lnk_path = get_startup_shortcut_path()
    lnk_path.parent.mkdir(parents=True, exist_ok=True)
    py_exe = resolve_python_executable()
    if _is_compiled():
        arg_parts = []
    else:
        target = target_script if target_script is not None else (WORKSPACE_DIR / "smart_shutdown.py")
        arg_parts = [f'"{str(target)}"']
    if mini_hud:
        arg_parts.append("--mini-hud")
    arg_parts.extend(["--countdown", str(countdown), "--idle-buffer", str(idle_buffer)])
    arguments = " ".join(arg_parts)
    ps_script = _build_startup_ps_script(lnk_path, py_exe, arguments)
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
        if res.returncode == 0 and lnk_path.exists():
            _unlink_legacy_shortcut(lnk_path.parent, logger)
            _log_startup_enabled(lnk_path, py_exe, arguments, logger)
            return True
        logger.error(f"[STARTUP_ERROR] Failed to create shortcut: {res.stderr}")
        print(f"[ERROR] Could not create startup shortcut: {res.stderr}")
    except Exception as e:
        logger.error(f"[STARTUP_ERROR] Failed to enable auto-startup: {e}")
        print(f"[ERROR] Failed to enable auto-startup: {e}")
    return False


def disable_startup(logger=None) -> bool:
    """Removes Smart Shutdown and legacy shortcuts from Windows Startup."""
    logger = logger or logging.getLogger("SmartShutdown")
    lnk_path = get_startup_shortcut_path()
    legacy_path = lnk_path.parent / LEGACY_STARTUP_SHORTCUT_NAME
    targets = [p for p in (lnk_path, legacy_path) if p.exists()]
    if not targets:
        print("\n" + "="*72)
        print("  ℹ️ Windows Auto-Startup is already DISABLED (no shortcut found).")
        print("="*72 + "\n")
        return True

    try:
        for target_path in targets:
            target_path.unlink(missing_ok=True)
            logger.info(f"[STARTUP] Windows Auto-Startup successfully DISABLED. Removed: {target_path}")
        print("\n" + "="*72)
        print("  ❌ WINDOWS AUTO-STARTUP SUCCESSFULLY DISABLED")
        print("="*72)
        for target_path in targets:
            print(f"  Removed Shortcut : {target_path}")
        print("="*72 + "\n")
        log_telemetry_event(logger, "STARTUP_DISABLED", {"shortcut": str(lnk_path), "shortcuts": [str(p) for p in targets]})
        return True
    except Exception as e:
        logger.error(f"[STARTUP_ERROR] Failed to remove shortcut: {e}")
        print(f"[ERROR] Failed to remove startup shortcut: {e}")
        return False


def toggle_startup(
    countdown: int = DEFAULT_COUNTDOWN_SECONDS,
    idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS,
    target_script: Path = None,
    mini_hud: bool = True,
    logger=None
) -> bool:
    """Toggles Windows Auto-Startup state between enabled and disabled."""
    if is_startup_enabled():
        return disable_startup(logger=logger)
    else:
        return enable_startup(countdown=countdown, idle_buffer=idle_buffer, target_script=target_script, mini_hud=mini_hud, logger=logger)


def reconcile_startup_shortcut(
    cfg: Any,
    logger: Optional[logging.Logger] = None,
    is_enabled_fn: Optional[Callable[[], bool]] = None,
    matches_fn: Optional[Callable[[int, int, bool], bool]] = None,
    enable_fn: Optional[Callable[..., bool]] = None,
    disable_fn: Optional[Callable[..., bool]] = None,
) -> None:
    """Align Windows Startup shortcut state and CLI flags with persisted SettingsConfig."""
    desired = bool(getattr(cfg, "start_with_windows", False))
    cd = int(cfg.master_shutdown_timer_min * 60)
    ib = int(cfg.user_inactivity_sec)
    mh = bool(getattr(cfg, "mini_hud_on_startup", True))
    check_enabled = is_enabled_fn or is_startup_enabled
    check_matches = matches_fn or startup_matches_settings
    run_enable = enable_fn or enable_startup
    run_disable = disable_fn or disable_startup
    if desired:
        if not check_enabled() or not check_matches(cd, ib, mh):
            run_enable(countdown=cd, idle_buffer=ib, mini_hud=mh, logger=logger)
    elif check_enabled():
        run_disable(logger=logger)


def show_startup_status(logger=None):
    """Displays current Windows Auto-Startup status and shortcut metadata."""
    enabled = is_startup_enabled()
    lnk_path = get_startup_shortcut_path()
    print("\n" + "="*72)
    print("  WINDOWS AUTO-STARTUP CONFIGURATION STATUS")
    print("="*72)
    print(f"  Current Status : {'ENABLED ✅' if enabled else 'DISABLED ❌'}")
    print(f"  Shortcut Path  : {lnk_path}")
    print(f"  File Exists    : {enabled}")
    if enabled:
        try:
            ps_cmd = f"$w = New-Object -ComObject WScript.Shell; $s = $w.CreateShortcut('{str(lnk_path)}'); Write-Output ('  Target Executable: ' + $s.TargetPath); Write-Output ('  Arguments        : ' + $s.Arguments); Write-Output ('  Working Directory: ' + $s.WorkingDirectory)"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                print(res.stdout.strip())
        except Exception:
            pass
    print("="*72 + "\n")
