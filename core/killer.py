# -*- coding: utf-8 -*-
"""
core.killer: Multi-layered forceful termination of open applications and visible windows at T-10 seconds.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import os
import csv
import io
import subprocess
import logging
from core.config import (
    CRITICAL_OS_WHITELIST,
    TARGETED_USER_APPS,
    get_parent_process_id,
    get_ancestor_process_ids,
    log_telemetry_event
)

def force_close_all_apps(dry_run: bool = False, logger=None) -> list:
    """
    Forcefully terminates open user applications and visible windows at T-10 seconds.
    Safely whitelists critical OS system processes and the running Python engine/parent launcher tree.
    In dry-run / test mode, enumerates and logs candidate processes without terminating them.

    Multi-Layered Termination Architecture (T-10s):
      Layer 1: Taskkill targeted desktop applications by executable name (/F /T /IM).
      Layer 2: PowerShell visible window nuke (Get-Process | Where-Object MainWindowHandle -ne 0 | Stop-Process -Force).
      Layer 3: Taskkill by PID for any enumerated user PID with visible window title.
    """
    logger = logger or logging.getLogger("SmartShutdown")
    current_pid = os.getpid()
    parent_pid = get_parent_process_id(current_pid)
    ancestor_pids = get_ancestor_process_ids(current_pid)

    # Protect current Python process, parent launcher, and OS kernel PIDs
    protected_pids = {current_pid, 0, 4} | ancestor_pids
    if parent_pid:
        protected_pids.add(parent_pid)

    candidates = []
    try:
        output = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/V"],
            text=True,
            errors="replace"
        )
        reader = csv.reader(io.StringIO(output))
        try:
            next(reader)  # skip header
        except StopIteration:
            pass

        for row in reader:
            if len(row) < 9:
                continue
            name = row[0].strip()
            name_lower = name.lower()
            try:
                pid = int(row[1].strip())
            except ValueError:
                continue
            title = row[8].strip()

            if pid in protected_pids:
                continue
            if name_lower in CRITICAL_OS_WHITELIST:
                continue
            # Also protect Python runtimes so the auto-shutdown countdown engine does not self-terminate
            if name_lower.startswith("python"):
                continue

            reason = None
            if name_lower in TARGETED_USER_APPS:
                reason = f"Targeted user application ({name})"
            elif title and title not in ("N/A", "", "Unknown"):
                reason = f"Visible window ({title})"

            if reason:
                candidates.append({
                    "pid": pid,
                    "name": name,
                    "title": title,
                    "reason": reason
                })
    except Exception as e:
        logger.error(f"[FORCE_CLOSE_ERROR] Failed to enumerate running processes: {e}")
        return []

    if dry_run:
        msg = f"[SAFE TEST / DRY RUN] T-10s Trigger: Simulating forceful termination of {len(candidates)} process(es)."
        logger.warning(msg)
        print("\n" + "="*72)
        print(f"  {msg}")
        print("  PC applications will NOT be terminated. Safe test simulation active.")
        print("="*72)
        for c in candidates:
            line = f"  [SIMULATED TERMINATION] PID {c['pid']:6d} | {c['name']:25s} | {c['reason']}"
            logger.info(line)
            print(line)
        print("="*72 + "\n")
        log_telemetry_event(logger, "FORCE_CLOSE_APPS_SIMULATED", {
            "dry_run": True,
            "count": len(candidates),
            "processes": [{"pid": c["pid"], "name": c["name"], "reason": c["reason"]} for c in candidates]
        })
        return candidates

    # Production Live Mode: Multi-layered Forceful Termination
    logger.critical(f"[FORCE_CLOSE] T-10s Trigger: Forcefully terminating all open applications and windows ({len(candidates)} candidates)...")
    killed = []

    # Layer 1: Targeted process termination by executable name
    targeted_to_kill = set(c["name"].lower() for c in candidates if c["name"].lower() in TARGETED_USER_APPS)
    shell_names = {"cmd.exe", "powershell.exe", "pwsh.exe"}

    for app_name in targeted_to_kill:
        if app_name in shell_names:
            continue
        try:
            logger.info(f"[FORCE_CLOSE_LAYER_1] Executing: taskkill /F /T /IM {app_name}")
            subprocess.run(["taskkill", "/F", "/T", "/IM", app_name], capture_output=True, text=True)
        except Exception as e:
            logger.warning(f"[FORCE_CLOSE_LAYER_1] Error executing taskkill on {app_name}: {e}")

    # Layer 2: PowerShell Visible Window Nuke
    try:
        protected_pids_csv = ",".join(str(p) for p in protected_pids)
        ps_cmd = (
            f"Get-Process | Where-Object {{ "
            f"$_.MainWindowHandle -ne 0 -and "
            f"$_.Id -notin @({protected_pids_csv}) -and "
            f"$_.ProcessName -notin @('explorer','dwm','python','pythonw') "
            f"}} | Stop-Process -Force"
        )
        logger.info("[FORCE_CLOSE_LAYER_2] Executing PowerShell visible window nuke...")
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            logger.info("[FORCE_CLOSE_LAYER_2] PowerShell visible window nuke executed successfully.")
        else:
            logger.debug(f"[FORCE_CLOSE_LAYER_2] PowerShell output: {res.stderr.strip()}")
    except Exception as e:
        logger.warning(f"[FORCE_CLOSE_LAYER_2] PowerShell window nuke encountered error: {e}")

    # Layer 3: Taskkill by PID for any enumerated candidate
    for c in candidates:
        pid = c["pid"]
        if pid in protected_pids:
            continue
        try:
            res = subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, text=True)
            if res.returncode == 0:
                killed.append(c)
                logger.info(f"[FORCE_CLOSE_LAYER_3] Terminated PID {pid} ({c['name']})")
        except Exception:
            pass

    log_telemetry_event(logger, "FORCE_CLOSE_APPS_EXECUTED", {
        "count": len(killed),
        "processes": [{"pid": c["pid"], "name": c["name"]} for c in killed]
    })
    return killed
