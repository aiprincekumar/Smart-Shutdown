# -*- coding: utf-8 -*-
"""
core.analyzer: Antigravity session analyzer and real-time transcript evaluator.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import os
import time
import json
import glob
import logging
from pathlib import Path
from core.config import (
    DEFAULT_BRAIN_DIR,
    DEFAULT_IDLE_BUFFER_SECONDS,
    DEFAULT_WINDOW_HOURS
)

class AntigravitySessionAnalyzer:
    """
    Scans and analyzes transcript.jsonl files within Antigravity brain sessions.
    Determines completion status, tool-call state, settling buffers, and user-wait states.
    """
    def __init__(self, brain_dir: Path = DEFAULT_BRAIN_DIR, window_hours: float = DEFAULT_WINDOW_HOURS,
                 start_timestamp: float = 0.0, filter_since_start: bool = False, logger=None):
        self.brain_dir = Path(brain_dir)
        self.window_hours = window_hours
        self.start_timestamp = start_timestamp
        self.filter_since_start = filter_since_start
        self.logger = logger or logging.getLogger("SmartShutdown")

    def scan_transcripts(self) -> list:
        """Finds all transcript.jsonl files within the brain folder."""
        if not self.brain_dir.exists():
            return []
        pattern = str(self.brain_dir / "*" / ".system_generated" / "logs" / "transcript.jsonl")
        return [Path(p) for p in glob.glob(pattern)]

    def analyze_transcript(self, file_path: Path, idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS) -> dict:
        """
        Inspects a single transcript.jsonl to determine its real-time state:
          - COMPLETED: Agent finished turn, status DONE, no tools pending, quiet for >= idle_buffer.
          - SETTLING: Agent finished turn, but quiet silence duration < idle_buffer.
          - BUSY: Agent actively running tools, subagent in flight, or status != DONE.
          - IN_FLIGHT: User prompt submitted, waiting for agent response.
          - WAITING_USER: Agent invoked 'ask_question' and is waiting for user response.
          - EMPTY: Blank transcript.
        """
        now = time.time()
        try:
            mtime = os.path.getmtime(file_path)
        except Exception as e:
            return {
                "status": "ERROR",
                "reason": f"Cannot read mtime: {e}",
                "silence": 0.0,
                "mtime": now,
                "step_index": None
            }

        silence = now - mtime

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = [l.strip() for l in f if l.strip()]
        except Exception as e:
            return {
                "status": "BUSY",
                "reason": f"Transcript locked for writing: {e}",
                "silence": silence,
                "mtime": mtime,
                "step_index": None
            }

        if not lines:
            return {
                "status": "EMPTY",
                "reason": "Transcript is empty",
                "silence": silence,
                "mtime": mtime,
                "step_index": None
            }

        # Parse the last valid step
        last_step = None
        for raw_line in reversed(lines[-10:]):
            try:
                last_step = json.loads(raw_line)
                break
            except Exception:
                continue

        if not last_step:
            return {
                "status": "BUSY",
                "reason": "Transcript actively being appended (JSON parse in flight)",
                "silence": silence,
                "mtime": mtime,
                "step_index": None
            }

        step_type = last_step.get("type")
        step_stat = last_step.get("status")
        step_idx = last_step.get("step_index")
        tool_calls = [c.get("tool_name") or c.get("name") for c in last_step.get("tool_calls", [])]

        effective_idle = idle_buffer if idle_buffer > 0 else 30

        # Condition 1: Step status not DONE
        if step_stat != "DONE":
            if silence >= effective_idle:
                return {
                    "status": "COMPLETED",
                    "reason": f"Step {step_idx} status '{step_stat}' but quiet for {silence:.0f}s (stopped/settled)",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }
            return {
                "status": "BUSY",
                "reason": f"Step {step_idx} status is '{step_stat}'",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }

        # Condition 2: Prompt in flight (USER_INPUT without subsequent response)
        if step_type == "USER_INPUT":
            if silence >= effective_idle:
                return {
                    "status": "COMPLETED",
                    "reason": f"User prompt settled/quiet for {silence:.0f}s",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }
            return {
                "status": "IN_FLIGHT",
                "reason": "Prompt in flight: User message waiting for agent response",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }

        # Condition 3: Intermediate tool result received, agent processing
        if step_type == "GENERIC":
            if silence >= effective_idle:
                return {
                    "status": "COMPLETED",
                    "reason": f"Tool result settled; quiet for {silence:.0f}s",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }
            return {
                "status": "BUSY",
                "reason": "Tool result received (GENERIC); agent currently processing next step",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }

        # Condition 4: System/Ephemeral message waiting for planner
        if step_type in ("SYSTEM_MESSAGE", "EPHEMERAL_MESSAGE"):
            if silence >= effective_idle:
                return {
                    "status": "COMPLETED",
                    "reason": f"{step_type} settled; quiet for {silence:.0f}s",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }
            return {
                "status": "BUSY",
                "reason": f"{step_type} posted; agent awaiting next planner cycle",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }

        # Condition 5: Planner response evaluation
        if step_type == "PLANNER_RESPONSE":
            if tool_calls:
                if "ask_question" in tool_calls:
                    return {
                        "status": "WAITING_USER",
                        "reason": "Interactive input pending: Waiting for user to answer 'ask_question'",
                        "silence": silence,
                        "mtime": mtime,
                        "step_index": step_idx
                    }
                if silence >= effective_idle:
                    return {
                        "status": "COMPLETED",
                        "reason": f"Tool execution ended/quiet for {silence:.0f}s",
                        "silence": silence,
                        "mtime": mtime,
                        "step_index": step_idx
                    }
                return {
                    "status": "BUSY",
                    "reason": f"Tool execution in flight: {tool_calls}",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }

            # PLANNER_RESPONSE with empty tool_calls and status DONE is COMPLETE!
            if silence < idle_buffer:
                return {
                    "status": "SETTLING",
                    "reason": f"Turn completed; awaiting silence buffer ({silence:.0f}s / {idle_buffer}s)",
                    "silence": silence,
                    "mtime": mtime,
                    "step_index": step_idx
                }
            return {
                "status": "COMPLETED",
                "reason": f"Turn completed; quiet for {silence:.0f}s",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }

        # Fallback
        if silence < idle_buffer:
            return {
                "status": "SETTLING",
                "reason": f"Recent step ({step_type}), awaiting silence buffer",
                "silence": silence,
                "mtime": mtime,
                "step_index": step_idx
            }
        return {
            "status": "COMPLETED",
            "reason": f"Idle for {silence:.0f}s",
            "silence": silence,
            "mtime": mtime,
            "step_index": step_idx
        }

    def evaluate_all(self, idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS) -> dict:
        """
        Evaluates all recent transcripts against completion criteria.
        Returns overall status and details of examined sessions.
        """
        now = time.time()
        window_cutoff = now - (self.window_hours * 3600)
        files = self.scan_transcripts()

        active_sessions = []
        for file_path in files:
            try:
                mtime = os.path.getmtime(file_path)
            except Exception:
                continue

            if self.filter_since_start:
                if mtime < self.start_timestamp:
                    continue
            else:
                if mtime < window_cutoff:
                    continue

            info = self.analyze_transcript(file_path, idle_buffer=idle_buffer)
            info["conversation_id"] = file_path.parent.parent.parent.name
            info["path"] = str(file_path)
            active_sessions.append(info)

        # Sort by mtime descending (most recent first)
        active_sessions.sort(key=lambda s: s.get("mtime", 0), reverse=True)

        if not active_sessions:
            return {
                "all_completed": True,
                "summary": "No recent Antigravity sessions in observation window.",
                "blocking_reason": None,
                "sessions": []
            }

        # Check for blocking sessions
        blocking = []
        for s in active_sessions:
            st = s.get("status")
            if st in ("BUSY", "IN_FLIGHT", "WAITING_USER", "SETTLING", "ERROR"):
                blocking.append(s)

        if blocking:
            lead = blocking[0]
            summary = f"Session {lead['conversation_id'][:8]}... is {lead['status']}: {lead['reason']}"
            return {
                "all_completed": False,
                "summary": summary,
                "blocking_reason": lead['reason'],
                "blocking_session": lead['conversation_id'],
                "sessions": active_sessions
            }

        return {
            "all_completed": True,
            "summary": f"All {len(active_sessions)} recent session(s) verified COMPLETE and idle for >= {idle_buffer}s.",
            "blocking_reason": None,
            "sessions": active_sessions
        }
