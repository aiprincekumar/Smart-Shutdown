# -*- coding: utf-8 -*-
"""
core.config: Global constants, telemetry logger, lock management, and settings persistence.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import os
import sys
import time
import json
import logging
import subprocess
import atexit
import ctypes
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional

from core.app_targets import (
    CRITICAL_OS_WHITELIST,
    TARGETED_USER_APPS,
    DEFAULT_APP_CLOSING_TARGETS,
    APP_PROCESS_MAPPING,
)
from core.models import DEFAULT_SIMULATION_SECONDS
from core.settings_store import load_settings_dict, save_json_dict_atomic

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def is_compiled_runtime() -> bool:
    """Return True when running from a frozen or Nuitka-compiled executable."""
    return bool(getattr(sys, "frozen", False) or "__compiled__" in globals())


IS_COMPILED = is_compiled_runtime()
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(sys.executable).resolve().parent if IS_COMPILED else WORKSPACE_DIR
DATA_DIR = (
    Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")) / "Smart Shutdown"
    if IS_COMPILED
    else WORKSPACE_DIR
)
if IS_COMPILED:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
DEFAULT_LOG_DIR = DATA_DIR / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "smart_shutdown.log"
LOCK_FILE = DATA_DIR / "smart_shutdown.lock"
DEFAULT_SETTINGS_FILE = DATA_DIR / "smart_shutdown_settings.json"
LEGACY_SETTINGS_FILE = DATA_DIR / "sentinel_settings.json"

DEFAULT_COUNTDOWN_SECONDS = 900
DEFAULT_IDLE_BUFFER_SECONDS = 60
DEFAULT_POLL_INTERVAL = 5
DEFAULT_WINDOW_HOURS = 2.0


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.c_size_t),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', ctypes.c_char * 260),
    ]


def get_parent_process_id(pid: int) -> Optional[int]:
    """Retrieves the parent process ID for a given PID using Toolhelp32 snapshot."""
    try:
        kernel32 = ctypes.windll.kernel32
        h_snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        if h_snapshot == -1:
            return None
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        ppid = None
        has_entry = bool(kernel32.Process32First(h_snapshot, ctypes.byref(pe)))
        while has_entry:
            if pe.th32ProcessID == pid:
                ppid = pe.th32ParentProcessID
                break
            has_entry = bool(kernel32.Process32Next(h_snapshot, ctypes.byref(pe)))
        kernel32.CloseHandle(h_snapshot)
        return ppid
    except Exception:
        return None


def get_ancestor_process_ids(pid: int) -> set:
    """Retrieves all ancestor process IDs up to kernel PIDs to protect parent launchers."""
    ancestors = set()
    curr = pid
    while curr:
        p = get_parent_process_id(curr)
        if not p or p in ancestors or p in (0, 4):
            break
        ancestors.add(p)
        curr = p
    return ancestors


def _read_lock_pid(logger=None) -> Optional[int]:
    """Read existing PID from LOCK_FILE if present and numeric."""
    if not LOCK_FILE.exists():
        return None
    try:
        raw = LOCK_FILE.read_text(encoding="utf-8").strip()
        return int(raw) if raw.isdigit() else None
    except Exception as e:
        if logger:
            logger.debug(f"[SINGLE_INSTANCE] Error reading existing lock: {e}")
        return None


def _is_smart_shutdown_pid(pid: int) -> bool:
    """Return True if PID is Python/Smart Shutdown; False if dead or unrelated."""
    try:
        import psutil
    except ImportError:
        return True
    try:
        proc = psutil.Process(pid)
        name = (proc.name() or "").lower()
    except psutil.NoSuchProcess:
        return False
    except Exception:
        return True
    if name.startswith("python") or "smart_shutdown" in name or "smartshutdown" in name:
        return True
    try:
        cmdline = " ".join(proc.cmdline() or ()).lower()
        return "smart_shutdown" in cmdline or "smartshutdown" in cmdline
    except Exception:
        return False


def _terminate_stale_instance(old_pid: int, my_pid: int, ancestors: set, logger=None) -> None:
    """Terminate an older sentinel instance if it is not self, kernel, or ancestor."""
    if old_pid == my_pid or old_pid <= 4 or old_pid in ancestors:
        return
    if not _is_smart_shutdown_pid(old_pid):
        if logger:
            logger.debug(f"[SINGLE_INSTANCE] Skipping non-SmartShutdown or dead PID {old_pid}")
        return
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        res = subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True, text=True, creationflags=flags)
        if logger and res.returncode == 0:
            logger.info(f"[SINGLE_INSTANCE] Terminated previous instance PID {old_pid} cleanly.")
        elif logger:
            logger.debug(f"[SINGLE_INSTANCE] taskkill PID {old_pid}: {res.stderr.strip()}")
    except Exception as e:
        if logger:
            logger.debug(f"[SINGLE_INSTANCE] Failed to terminate old PID {old_pid}: {e}")
    time.sleep(0.2)


def acquire_single_instance_lock(logger=None) -> None:
    """Ensure only one sentinel instance runs by replacing any stale lock owner."""
    my_pid = os.getpid()
    old_pid = _read_lock_pid(logger=logger)
    if old_pid is not None:
        _terminate_stale_instance(old_pid, my_pid, get_ancestor_process_ids(my_pid), logger=logger)
    try:
        LOCK_FILE.write_text(str(my_pid), encoding="utf-8")
        if logger:
            logger.debug(f"[SINGLE_INSTANCE] Acquired single-instance lock for PID {my_pid}")
    except Exception as e:
        if logger:
            logger.warning(f"[SINGLE_INSTANCE] Could not write lock file: {e}")
    atexit.register(release_single_instance_lock, logger=logger)


def release_single_instance_lock(logger=None) -> None:
    """Releases the single-instance lock file upon process exit."""
    try:
        if not LOCK_FILE.exists():
            return
        my_pid = os.getpid()
        if LOCK_FILE.read_text(encoding="utf-8").strip() == str(my_pid):
            LOCK_FILE.unlink(missing_ok=True)
            if logger:
                logger.debug(f"[SINGLE_INSTANCE] Released single-instance lock for PID {my_pid}")
    except Exception:
        pass


def _match_app_target(pname: str, title: str, app_targets: Dict[str, bool]) -> Optional[bool]:
    """Match process name or window title against APP_PROCESS_MAPPING target entries."""
    for app_name, spec in APP_PROCESS_MAPPING.items():
        if app_name == "AntiGravity":
            continue
        if pname not in spec["processes"] and not any(kw in pname or kw in title for kw in spec["keywords"]):
            continue
        if app_name in app_targets:
            return bool(app_targets[app_name])
        if app_name == "Adobe Acrobat Reader" and "Adobe Acrobat" in app_targets:
            return bool(app_targets["Adobe Acrobat"])
        if app_name == "Opera Browser" and "Opera" in app_targets:
            return bool(app_targets["Opera"])
        return True
    return None


def should_close_process(
    process_name: str,
    window_title: str,
    app_targets: Optional[Dict[str, bool]] = None,
    close_antigravity: bool = True,
) -> bool:
    """Determine whether a process/window should be closed based on user app closing settings."""
    pname = (process_name or "").strip().lower()
    title = (window_title or "").strip().lower()

    if pname == "antigravity.exe" or "antigravity" in pname or "antigravity" in title:
        if not close_antigravity:
            return False
        if app_targets is not None and app_targets.get("AntiGravity") is False:
            return False
        return True

    if app_targets is None:
        return True
    if pname in app_targets:
        return bool(app_targets[pname])
    if process_name in app_targets:
        return bool(app_targets[process_name])

    matched = _match_app_target(pname, title, app_targets)
    if matched is not None:
        return matched
    if window_title in app_targets:
        return bool(app_targets[window_title])
    if title in app_targets:
        return bool(app_targets[title])
    return True


def setup_logger(log_file: Path = DEFAULT_LOG_FILE, debug: bool = False) -> logging.Logger:
    """Initializes and returns the standardized UTF-8 logger."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("SmartShutdown")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    for handler in (logging.FileHandler(str(log_file), encoding="utf-8"), logging.StreamHandler(sys.stdout)):
        handler.setLevel(logging.DEBUG if debug else logging.INFO)
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


def log_telemetry_event(logger: logging.Logger, event_name: str, payload: dict) -> None:
    """Logs structured JSON event payload per Dept 14 specification."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "event": event_name,
        "service": "smart-shutdown",
        "payload": payload,
    }
    logger.info(f"[TELEMETRY] {json.dumps(record, ensure_ascii=False)}")


@dataclass
class SettingsConfig:
    """Holds configuration parameters for Smart Shutdown."""
    user_inactivity_sec: int = 60
    ai_recheck_interval_min: int = 5
    master_shutdown_timer_min: int = 15
    simulation_timer_sec: int = DEFAULT_SIMULATION_SECONDS
    pre_shutdown_close_window_sec: int = 30
    waiting_mode: str = "Hybrid"
    waiting_hybrid_timeout_min: int = 10
    cpu_threshold_pct: float = 15.0
    network_threshold_kb: float = 50.0
    audio_inhibit_enabled: bool = True
    start_with_windows: bool = False
    minimize_to_tray: bool = True
    mini_hud_on_startup: bool = True
    target_action: str = "Shutdown"
    execution_mode: str = "Live"
    close_antigravity: bool = True
    app_closing_targets: Dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_APP_CLOSING_TARGETS))

    def _sync_app_targets(self) -> None:
        """Validate app_closing_targets keys and keep AntiGravity flags synchronized."""
        if not isinstance(self.app_closing_targets, dict):
            self.app_closing_targets = dict(DEFAULT_APP_CLOSING_TARGETS)
        for k, v in DEFAULT_APP_CLOSING_TARGETS.items():
            self.app_closing_targets[k] = bool(self.app_closing_targets[k]) if k in self.app_closing_targets else v
        self.close_antigravity = bool(self.close_antigravity)
        if "AntiGravity" not in self.app_closing_targets:
            return
        if not self.close_antigravity:
            self.app_closing_targets["AntiGravity"] = False
        else:
            self.close_antigravity = bool(self.app_closing_targets["AntiGravity"])

    def clamp(self) -> None:
        """Clamp parameters within valid ranges."""
        self.user_inactivity_sec = max(10, min(7200, int(self.user_inactivity_sec)))
        self.ai_recheck_interval_min = max(1, min(30, int(self.ai_recheck_interval_min)))
        self.master_shutdown_timer_min = max(1, min(60, int(self.master_shutdown_timer_min)))
        self.simulation_timer_sec = max(10, min(3600, int(getattr(self, "simulation_timer_sec", DEFAULT_SIMULATION_SECONDS))))
        self.pre_shutdown_close_window_sec = max(10, min(120, int(self.pre_shutdown_close_window_sec)))
        if self.waiting_mode not in ("Unlimited", "Timer", "Hybrid"):
            self.waiting_mode = "Hybrid"
        self.waiting_hybrid_timeout_min = max(1, min(60, int(self.waiting_hybrid_timeout_min)))
        self.cpu_threshold_pct = max(1.0, min(100.0, float(getattr(self, "cpu_threshold_pct", 15.0))))
        self.network_threshold_kb = max(0.0, min(10000.0, float(getattr(self, "network_threshold_kb", 50.0))))
        if getattr(self, "target_action", "Shutdown") not in ("Shutdown", "Hibernate", "Sleep", "Lock Screen"):
            self.target_action = "Shutdown"
        if getattr(self, "execution_mode", "Live") not in ("Live", "Demo (30s)", "Demo (10s)", "Simulation"):
            self.execution_mode = "Live"
        self._sync_app_targets()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettingsConfig":
        """Instantiate configuration from dictionary with clamped values."""
        data = data or {}
        close_ag = data.get("close_antigravity")
        raw_targets = data.get("app_closing_targets")
        targets = dict(DEFAULT_APP_CLOSING_TARGETS)
        if isinstance(raw_targets, dict):
            for k, v in raw_targets.items():
                targets[k] = bool(v)

        if close_ag is not None:
            close_antigravity = bool(close_ag)
            targets["AntiGravity"] = close_antigravity
        else:
            close_antigravity = bool(targets.get("AntiGravity", True))

        cfg = cls(
            user_inactivity_sec=int(data.get("user_inactivity_sec", 60)),
            ai_recheck_interval_min=int(data.get("ai_recheck_interval_min", 5)),
            master_shutdown_timer_min=int(data.get("master_shutdown_timer_min", 15)),
            simulation_timer_sec=int(data.get("simulation_timer_sec", DEFAULT_SIMULATION_SECONDS)),
            pre_shutdown_close_window_sec=int(data.get("pre_shutdown_close_window_sec", 30)),
            waiting_mode=str(data.get("waiting_mode", "Hybrid")),
            waiting_hybrid_timeout_min=int(data.get("waiting_hybrid_timeout_min", 10)),
            cpu_threshold_pct=float(data.get("cpu_threshold_pct", 15.0)),
            network_threshold_kb=float(data.get("network_threshold_kb", 50.0)),
            audio_inhibit_enabled=bool(data.get("audio_inhibit_enabled", True)),
            start_with_windows=bool(data.get("start_with_windows", False)),
            minimize_to_tray=bool(data.get("minimize_to_tray", True)),
            mini_hud_on_startup=bool(data.get("mini_hud_on_startup", True)),
            target_action=str(data.get("target_action", "Shutdown")),
            execution_mode=str(data.get("execution_mode", "Live")),
            close_antigravity=close_antigravity,
            app_closing_targets=targets,
        )
        cfg.clamp()
        return cfg


def load_settings_config(settings_path: Optional[Path] = None) -> SettingsConfig:
    """Load SettingsConfig from atomic UTF-8 BOM store with backup and legacy fallback."""
    path = Path(settings_path) if settings_path is not None else DEFAULT_SETTINGS_FILE
    log = logging.getLogger("SmartShutdown")
    data = load_settings_dict(path, legacy=LEGACY_SETTINGS_FILE, allow_legacy=(settings_path is None), logger=log)
    if data is not None:
        return SettingsConfig.from_dict(data)
    cfg = SettingsConfig()
    cfg.clamp()
    return cfg


def save_settings_config(config: SettingsConfig, settings_path: Optional[Path] = None) -> bool:
    """Persist clamped SettingsConfig atomically with UTF-8 BOM and .bak rotation."""
    path = Path(settings_path) if settings_path is not None else DEFAULT_SETTINGS_FILE
    config.clamp()
    return save_json_dict_atomic(path, config.to_dict(), logger=logging.getLogger("SmartShutdown"))
