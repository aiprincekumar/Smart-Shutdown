# -*- coding: utf-8 -*-
"""
core: Smart Shutdown Modular Framework.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from core.config import (
    WORKSPACE_DIR,
    DEFAULT_BRAIN_DIR,
    DEFAULT_LOG_DIR,
    DEFAULT_LOG_FILE,
    DEFAULT_SETTINGS_FILE,
    LOCK_FILE,
    DEFAULT_COUNTDOWN_SECONDS,
    DEFAULT_IDLE_BUFFER_SECONDS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_WINDOW_HOURS,
    PROCESSENTRY32,
    CRITICAL_OS_WHITELIST,
    TARGETED_USER_APPS,
    get_parent_process_id,
    get_ancestor_process_ids,
    acquire_single_instance_lock,
    release_single_instance_lock,
    setup_logger,
    log_telemetry_event,
    SettingsConfig,
    load_settings_config,
    save_settings_config,
)

from core.console import hide_console_window
from core.audio import play_sound_alert, play_tick_sound, play_reset_sound, is_audio_stream_active
from core.win32_window import make_hwnd_topmost
from core.killer import force_close_all_apps
from core.analyzer import AntigravitySessionAnalyzer
from core.shutdown import execute_system_shutdown
from core.gui import CountdownWindow
from core.startup import (
    get_startup_shortcut_path,
    is_startup_enabled,
    enable_startup,
    disable_startup,
    toggle_startup,
    show_startup_status
)
from core.monitor import run_monitor_loop

# Phase 01: Physical Input Hook
from core.input_hook import (
    get_idle_seconds,
    is_user_idle,
    get_last_input_tick,
    get_last_input_timestamp
)

# Phase 02: Transcript Sentinel & Process Tree
from core.transcript_sentinel import TranscriptSentinel
from core.process_tree import (
    is_antigravity_active,
    is_process_tree_busy,
    find_antigravity_root_pids,
    get_descendant_processes
)

# Phase 03: Waiting Gate & Hybrid Model
from core.waiting_gate import (
    WaitingMode,
    WaitingResult,
    evaluate_waiting_state,
    is_interactive_prompt_pending
)

# Phase 05: Pre-Shutdown App Closer & Shutdown Dispatcher
from core.app_closer import (
    enumerate_user_windows,
    close_user_applications,
    close_antigravity_cleanly,
    is_running_under_test
)
from core.shutdown_dispatcher import (
    execute_shutdown,
    abort_shutdown
)

# Phase 06: Unified 4-Layer Lifecycle Coordinator
from core.telemetry_collector import TelemetryCollector
from core.coordinator import (
    LifecycleState,
    SentinelCoordinator
)

__all__ = [
    "WORKSPACE_DIR",
    "DEFAULT_BRAIN_DIR",
    "DEFAULT_LOG_DIR",
    "DEFAULT_LOG_FILE",
    "DEFAULT_SETTINGS_FILE",
    "LOCK_FILE",
    "DEFAULT_COUNTDOWN_SECONDS",
    "DEFAULT_IDLE_BUFFER_SECONDS",
    "DEFAULT_POLL_INTERVAL",
    "DEFAULT_WINDOW_HOURS",
    "PROCESSENTRY32",
    "CRITICAL_OS_WHITELIST",
    "TARGETED_USER_APPS",
    "get_parent_process_id",
    "get_ancestor_process_ids",
    "acquire_single_instance_lock",
    "release_single_instance_lock",
    "setup_logger",
    "log_telemetry_event",
    "hide_console_window",
    "play_sound_alert",
    "play_tick_sound",
    "play_reset_sound",
    "is_audio_stream_active",
    "make_hwnd_topmost",
    "force_close_all_apps",
    "AntigravitySessionAnalyzer",
    "execute_system_shutdown",
    "CountdownWindow",
    "get_startup_shortcut_path",
    "is_startup_enabled",
    "enable_startup",
    "disable_startup",
    "toggle_startup",
    "show_startup_status",
    "run_monitor_loop",
    "get_idle_seconds",
    "is_user_idle",
    "get_last_input_tick",
    "get_last_input_timestamp",
    "TranscriptSentinel",
    "is_antigravity_active",
    "is_process_tree_busy",
    "find_antigravity_root_pids",
    "get_descendant_processes",
    "WaitingMode",
    "WaitingResult",
    "evaluate_waiting_state",
    "is_interactive_prompt_pending",
    "enumerate_user_windows",
    "close_user_applications",
    "close_antigravity_cleanly",
    "is_running_under_test",
    "execute_shutdown",
    "abort_shutdown",
    "LifecycleState",
    "TelemetryCollector",
    "SentinelCoordinator",
    "SettingsConfig",
    "load_settings_config",
    "save_settings_config",
]
