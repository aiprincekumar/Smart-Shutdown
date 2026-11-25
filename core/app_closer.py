# -*- coding: utf-8 -*-
"""
core.app_closer: Desktop window enumeration and graceful application closure via WM_CLOSE.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

Safely enumerates visible user desktop windows and posts polite WM_CLOSE (0x0010)
messages during the pre-shutdown grace window while strictly protecting system PIDs.
"""

import os
import sys
import inspect
import logging
from typing import List, Dict, Any, Set, Optional, Tuple
import psutil

from core.config import (
    CRITICAL_OS_WHITELIST,
    log_telemetry_event,
    should_close_process,
)
from core.process_tree import get_protected_pids

WM_CLOSE: int = 0x0010
DESKTOP_ENUMERATE: int = 0x0100
_SHELL_PROTECTED_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}

logger_instance = logging.getLogger("SmartShutdown")
get_safeguarded_pids = get_protected_pids


def is_running_under_test() -> bool:
    """
    Multi-vector detection to determine if code is executing within an automated test framework.
    Protects developer and agent IDE sessions from accidental termination during test runs.
    """
    if os.environ.get("ANTIGRAVITY_TEST_MODE") == "1":
        return True
    if os.environ.get("PYTEST_CURRENT_TEST") or ("pytest" in sys.modules):
        return True
    if hasattr(sys, "argv") and sys.argv:
        argv_str = " ".join(sys.argv).lower()
        if any(marker in argv_str for marker in ("unittest", "pytest", "discover", "test_")):
            return True
    try:
        for frame in inspect.stack():
            fname = frame.filename.lower()
            if any(marker in fname for marker in ("unittest", "pytest", "\\tests\\", "/tests/", "test_")):
                return True
    except Exception:
        pass
    return False


def _get_window_info(user32, hwnd: int) -> Optional[Dict[str, Any]]:
    """Inspects a window handle and returns its PID, title, class name, and visibility."""
    import ctypes
    from ctypes import wintypes

    if not user32.IsWindowVisible(hwnd):
        return None

    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return None

    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value.strip()
    if not title or title in ("Program Manager", "N/A", "Unknown"):
        return None

    class_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_buf, 256)
    win_class = class_buf.value.strip()

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return {"hwnd": hwnd, "pid": pid.value, "title": title, "win_class": win_class}


def _inspect_desktop_window(user32, hwnd: int, protected: Set[int]) -> Optional[Dict[str, Any]]:
    """Filter and enrich a single desktop window handle if it is a closeable user app."""
    info = _get_window_info(user32, hwnd)
    if not info or info["pid"] in protected:
        return None
    win_class = info.get("win_class", "")
    if win_class in _SHELL_PROTECTED_CLASSES:
        return None
    try:
        p = psutil.Process(info["pid"])
        name = p.name().lower()
        if name.startswith("python"):
            return None
        if name == "explorer.exe":
            if win_class not in ("CabinetWClass", "ExploreWClass"):
                return None
            info["process_name"] = "explorer.exe"
            return info
        if name in CRITICAL_OS_WHITELIST:
            return None
        info["process_name"] = p.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        info["process_name"] = "unknown"
    return info


def enumerate_user_windows(protected_pids: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
    """
    Enumerates all visible top-level user desktop windows.
    Filters out system processes, protected PIDs, and the sentinel process tree.
    Allows visible File Explorer folder windows while strictly protecting shell/taskbar.
    """
    if sys.platform != "win32":
        return []

    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    protected = protected_pids if protected_pids is not None else get_safeguarded_pids()
    windows: List[Dict[str, Any]] = []

    def enum_handler(hwnd, lparam):
        info = _inspect_desktop_window(user32, hwnd, protected)
        if info:
            windows.append(info)
        return True

    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(enum_handler)
    hdesk = user32.OpenInputDesktop(0, False, DESKTOP_ENUMERATE)
    if hdesk:
        user32.EnumDesktopWindows(hdesk, proc, 0)
        user32.CloseDesktop(hdesk)
    else:
        user32.EnumWindows(proc, 0)
    return windows


def _resolve_target_filter(
    config: Optional[Any],
    app_targets: Optional[Dict[str, bool]],
    close_antigravity: bool,
) -> Tuple[Optional[Dict[str, bool]], bool]:
    """Extract effective app target filters and close_antigravity preference."""
    if config is None:
        return app_targets, close_antigravity
    if app_targets is None and hasattr(config, "app_closing_targets"):
        app_targets = getattr(config, "app_closing_targets", None)
    if hasattr(config, "close_antigravity"):
        close_antigravity = bool(getattr(config, "close_antigravity", True))
    return app_targets, close_antigravity


def _filter_close_candidates(
    candidates: List[Dict[str, Any]],
    app_targets: Optional[Dict[str, bool]],
    close_antigravity: bool,
    log: logging.Logger,
) -> List[Dict[str, Any]]:
    """Filter candidate windows by user target configuration and test-mode guards."""
    under_test = is_running_under_test()
    filtered: List[Dict[str, Any]] = []
    for item in candidates:
        pname = str(item.get("process_name", ""))
        title = str(item.get("title", ""))
        if not should_close_process(pname, title, app_targets=app_targets, close_antigravity=close_antigravity):
            log.info(f"[APP_CLOSER_FILTER] Skipping unchecked app: PID {item.get('pid')} | App: '{pname}' | Title: '{title}'")
            continue
        if under_test and ("antigravity" in pname.lower() or "antigravity" in title.lower()):
            log.info(f"[APP_CLOSER_TEST_GUARD] Excluding Antigravity window: PID {item.get('pid')} | Title: '{title}'")
            continue
        filtered.append(item)
    return filtered


def _dispatch_wm_close(
    candidates: List[Dict[str, Any]],
    dry_run: bool,
    log: logging.Logger,
) -> List[Dict[str, Any]]:
    """Log dry-run candidates or dispatch polite WM_CLOSE messages in live mode."""
    if dry_run:
        log.warning(f"[APP_CLOSER_SIMULATION] Found {len(candidates)} visible window(s). Simulation mode active.")
        for item in candidates:
            log.info(f"  [SIMULATED WM_CLOSE] PID: {item['pid']} | App: {item.get('process_name')} | Title: {item['title']}")
        return candidates

    import ctypes
    user32 = ctypes.windll.user32
    log.info(f"[APP_CLOSER] Sending polite WM_CLOSE to {len(candidates)} visible application(s)...")
    for item in candidates:
        log.info(f"  [WM_CLOSE] Dispatching to PID {item['pid']} ({item.get('process_name', 'unknown')}): '{item['title']}'")
        user32.PostMessageW(item["hwnd"], WM_CLOSE, 0, 0)
    log_telemetry_event(log, "WM_CLOSE_DISPATCHED", {"count": len(candidates)})
    return candidates


def close_user_applications(
    dry_run: bool = False,
    protected_pids: Optional[Set[int]] = None,
    logger: Optional[logging.Logger] = None,
    app_targets: Optional[Dict[str, bool]] = None,
    close_antigravity: bool = True,
    config: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Posts polite WM_CLOSE messages to visible user applications honoring config and test guards."""
    log = logger or logger_instance
    candidates = enumerate_user_windows(protected_pids=protected_pids)
    targets, allow_ag = _resolve_target_filter(config, app_targets, close_antigravity)
    filtered = _filter_close_candidates(candidates, targets, allow_ag, log)
    return _dispatch_wm_close(filtered, dry_run, log)


def close_antigravity_cleanly(
    dry_run: bool = False,
    force_test_allow: bool = False,
    logger: Optional[logging.Logger] = None,
    enabled: bool = True,
    close_antigravity: Optional[bool] = None,
) -> bool:
    """Finds running Antigravity processes and requests graceful exit."""
    log = logger or logger_instance
    if close_antigravity is not None:
        enabled = close_antigravity
    if not enabled:
        log.info("[APP_CLOSER] AntiGravity closure disabled by user settings. Skipping termination.")
        return False
    if is_running_under_test() and not force_test_allow:
        log.warning("[APP_CLOSER_TEST_GUARD] Automated test run detected. PERMANENTLY SKIPPING Antigravity termination.")
        return False

    closed_any = False
    protected = get_safeguarded_pids()
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            name = proc.info.get("name", "").lower()
            pid = proc.info.get("pid")
            if "antigravity" not in name or pid in protected:
                continue
            if dry_run:
                log.info(f"  [SIMULATED ANTIGRAVITY CLOSE] PID {pid} ({proc.info['name']})")
            else:
                log.info(f"  [TERMINATE ANTIGRAVITY] PID {pid} ({proc.info['name']})")
                proc.terminate()
            closed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return closed_any
