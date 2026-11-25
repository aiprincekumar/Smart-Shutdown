# -*- coding: utf-8 -*-
"""
core.process_tree: AntiGravity process hierarchy inspection and activity evaluation.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

Traverses process trees via psutil to detect active child worker processes (compilers,
test runners, node, git) spawned by AntiGravity while safeguarding sentinel runtimes.
"""

import os
import logging
from pathlib import Path
from typing import List, Set, Optional, Dict, Any, Tuple
import psutil

from core.config import (
    DEFAULT_IDLE_BUFFER_SECONDS,
    get_parent_process_id,
    get_ancestor_process_ids,
)
from core.transcript_sentinel import TranscriptSentinel

logger_instance = logging.getLogger("SmartShutdown")
_PROC_CACHE: Dict[int, psutil.Process] = {}


def get_protected_pids() -> Set[int]:
    """Returns the set of protected PIDs (sentinel, launcher, OS system roots)."""
    curr = os.getpid()
    parent = get_parent_process_id(curr)
    ancestors = get_ancestor_process_ids(curr)
    protected = {0, 4, curr} | ancestors
    if parent:
        protected.add(parent)
    return protected


def find_antigravity_root_pids() -> List[int]:
    """Finds all root process IDs for running Antigravity instances."""
    root_pids = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            name = proc.info.get("name", "").lower()
            if "antigravity" in name:
                root_pids.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return root_pids


def get_descendant_processes(root_pids: List[int]) -> List[psutil.Process]:
    """Retrieves all recursive child processes spawned by the specified root PIDs."""
    descendants = []
    protected = get_protected_pids()

    for pid in root_pids:
        if pid in protected:
            continue
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                if child.pid not in protected:
                    descendants.append(child)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return descendants


def is_process_busy(proc: psutil.Process, cpu_threshold: float = 1.5) -> bool:
    """Checks whether a single process is actively executing work."""
    try:
        status = proc.status()
        if status in (psutil.STATUS_RUNNING, psutil.STATUS_DISK_SLEEP):
            cpu = proc.cpu_percent(interval=0.05)
            if cpu >= cpu_threshold:
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return False


def is_process_tree_busy(cpu_threshold: float = 1.5) -> bool:
    """
    Checks if any descendant process under Antigravity is actively executing
    tasks, compiling code, or running test runners.
    """
    roots = find_antigravity_root_pids()
    if not roots:
        return False

    for p in get_descendant_processes(roots):
        if is_process_busy(p, cpu_threshold=cpu_threshold):
            return True
    return False


def _resolve_cached_process(proc: psutil.Process) -> psutil.Process:
    """Reuse cached psutil.Process instance when PID and create_time match."""
    if type(proc) is not psutil.Process:
        return proc
    pid = proc.pid
    cached = _PROC_CACHE.get(pid)
    if cached is not None:
        try:
            if cached.create_time() == proc.create_time():
                return cached
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _PROC_CACHE[pid] = proc
    return proc


def _sample_process_metric(proc: psutil.Process, cpu_threshold: float) -> Tuple[bool, int]:
    """Sample non-blocking CPU activity and RSS memory bytes for one process."""
    target = _resolve_cached_process(proc)
    try:
        mem_info = target.memory_info()
        rss = int(getattr(mem_info, "rss", 0) or 0)
        status = target.status()
        cpu = float(target.cpu_percent(interval=None) or 0.0)
        is_busy = status in (psutil.STATUS_RUNNING, psutil.STATUS_DISK_SLEEP) and cpu >= cpu_threshold
        return is_busy, max(0, rss)
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
        return False, 0


def get_process_tree_telemetry(cpu_threshold: float = 1.5) -> Dict[str, Any]:
    """Collect non-blocking descendant PIDs, worker count, RAM usage, and busy flag."""
    roots = find_antigravity_root_pids()
    if not roots:
        _PROC_CACHE.clear()
        return {"active_pids": [], "worker_count": 0, "memory_mb": 0, "is_tree_busy": False}

    descendants = get_descendant_processes(roots)
    seen_pids: Set[int] = set()
    active_pids: List[int] = []
    total_rss = 0

    for proc in descendants:
        pid = proc.pid
        if pid in seen_pids:
            continue
        seen_pids.add(pid)
        is_busy, rss = _sample_process_metric(proc, cpu_threshold)
        total_rss += rss
        if is_busy:
            active_pids.append(pid)

    for stale_pid in [pid for pid in _PROC_CACHE if pid not in seen_pids]:
        _PROC_CACHE.pop(stale_pid, None)

    return {
        "active_pids": active_pids,
        "worker_count": len(active_pids),
        "memory_mb": int(total_rss // (1024 * 1024)),
        "is_tree_busy": bool(active_pids),
    }


def is_antigravity_active(
    brain_dir: Optional[Path] = None,
    idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS,
    check_processes: bool = True,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """
    Unified evaluation returning True if AntiGravity is currently active:
      1. Live transcript shows in-flight tasks, pending tools, or settling turn.
      2. Descendant child processes are actively burning CPU / running tests.
    """
    log = logger or logger_instance
    eval_res = TranscriptSentinel(brain_dir=brain_dir, logger=log).evaluate_all(idle_buffer=idle_buffer)

    if not eval_res["all_completed"]:
        log.debug(f"[ACTIVE] Transcripts busy: {eval_res['summary']}")
        return True

    if check_processes and is_process_tree_busy():
        log.debug("[ACTIVE] Descendant worker processes are executing tasks")
        return True

    return False
