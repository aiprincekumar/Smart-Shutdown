# -*- coding: utf-8 -*-
"""
core.transcript_sentinel: Real-time AntiGravity session transcript monitoring.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)

Parses live conversation transcripts (~/.gemini/antigravity/brain/*/transcript.jsonl)
to evaluate in-flight tool calls, planner responses, settling buffers, and completion.
"""

import os
import glob
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.config import DEFAULT_BRAIN_DIR, DEFAULT_IDLE_BUFFER_SECONDS, DEFAULT_WINDOW_HOURS

logger_instance = logging.getLogger("SmartShutdown")

class TranscriptSentinel:
    """
    Monitors and parses AntiGravity conversation transcript.jsonl files
    to accurately detect active vs completed agent tasks.
    """

    def __init__(
        self,
        brain_dir: Optional[Path] = None,
        window_hours: float = DEFAULT_WINDOW_HOURS,
        start_timestamp: float = 0.0,
        filter_since_start: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        self.brain_dir = Path(brain_dir) if brain_dir else DEFAULT_BRAIN_DIR
        self.window_hours = float(window_hours)
        self.start_timestamp = float(start_timestamp)
        self.filter_since_start = filter_since_start
        self.logger = logger or logger_instance

    def scan_transcripts(self) -> List[Path]:
        """Finds all transcript.jsonl files within the brain directory."""
        if not self.brain_dir.exists():
            return []
        pattern = str(self.brain_dir / "*" / ".system_generated" / "logs" / "transcript.jsonl")
        return [Path(p) for p in glob.glob(pattern)]

    def _extract_recent_lines(self, file_path: Path, max_lines: int = 15) -> List[str]:
        """Reads the tail lines of a transcript file safely using a 32 KB tail seek."""
        try:
            with open(file_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                if file_size <= 0:
                    return []
                offset = max(0, file_size - 32768)
                f.seek(offset, os.SEEK_SET)
                text = f.read().decode("utf-8", errors="replace")
            raw_lines = text.splitlines()
            if offset > 0 and len(raw_lines) > 1:
                raw_lines = raw_lines[1:]
            lines = [line.strip().lstrip("\ufeff") for line in raw_lines if line.strip()]
            return lines[-max_lines:] if len(lines) > max_lines else lines
        except Exception as err:
            self.logger.debug(f"[SENTINEL] Could not read {file_path}: {err}")
            return []

    def _parse_last_json_step(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Parses the most recent valid JSON line from the tail lines."""
        for raw in reversed(lines):
            try:
                return json.loads(raw)
            except Exception:
                continue
        return None

    def _classify_step(
        self,
        step: Dict[str, Any],
        silence: float,
        effective_idle: int
    ) -> Dict[str, Any]:
        """Classifies the agent state based on the last recorded step in transcript."""
        step_type = step.get("type", "UNKNOWN")
        step_stat = step.get("status", "UNKNOWN")
        step_idx = step.get("step_index")
        calls = [c.get("tool_name") or c.get("name") for c in step.get("tool_calls", [])]

        if step_stat != "DONE":
            if silence >= effective_idle:
                return {"status": "COMPLETED", "reason": f"Step {step_idx} status '{step_stat}' settled ({silence:.0f}s)"}
            return {"status": "BUSY", "reason": f"Step {step_idx} status is '{step_stat}' (in-flight)"}

        if step_type == "USER_INPUT":
            if silence >= effective_idle:
                return {"status": "COMPLETED", "reason": f"User prompt settled ({silence:.0f}s)"}
            return {"status": "IN_FLIGHT", "reason": "User prompt submitted, awaiting agent response"}

        if step_type in ("GENERIC", "SYSTEM_MESSAGE", "EPHEMERAL_MESSAGE"):
            if silence >= effective_idle:
                return {"status": "COMPLETED", "reason": f"{step_type} settled ({silence:.0f}s)"}
            return {"status": "BUSY", "reason": f"{step_type} in progress"}

        if step_type == "PLANNER_RESPONSE":
            if calls and "ask_question" in calls:
                return {"status": "WAITING_USER", "reason": "Waiting for user input on 'ask_question'"}
            if calls:
                if silence >= effective_idle:
                    return {"status": "COMPLETED", "reason": f"Tool execution completed/quiet ({silence:.0f}s)"}
                return {"status": "BUSY", "reason": f"Executing tools: {', '.join(str(c) for c in calls if c)}"}
            if silence < effective_idle:
                return {"status": "SETTLING", "reason": f"Agent finished; settling ({silence:.0f}s/{effective_idle}s)"}
            return {"status": "COMPLETED", "reason": f"Turn complete; quiet for {silence:.0f}s"}

        return {"status": "COMPLETED", "reason": f"Step type {step_type} settled"}

    def evaluate_session(
        self,
        file_path: Path,
        idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS
    ) -> Dict[str, Any]:
        """Inspects a single transcript.jsonl and returns its current state."""
        now = time.time()
        effective_idle = max(10, idle_buffer)
        conv_id = file_path.parent.parent.name if file_path.parent.name == "logs" else file_path.parent.name

        try:
            mtime = os.path.getmtime(file_path)
        except Exception as e:
            return {"conversation_id": conv_id, "status": "ERROR", "reason": str(e), "silence": 0.0, "mtime": now}

        silence = now - mtime
        lines = self._extract_recent_lines(file_path)
        if not lines:
            return {"conversation_id": conv_id, "status": "EMPTY", "reason": "Transcript empty", "silence": silence, "mtime": mtime}

        step = self._parse_last_json_step(lines)
        if not step:
            return {"conversation_id": conv_id, "status": "BUSY", "reason": "Parsing step in flight", "silence": silence, "mtime": mtime}

        classification = self._classify_step(step, silence, effective_idle)
        return {
            "conversation_id": conv_id,
            "status": classification["status"],
            "reason": classification["reason"],
            "silence": silence,
            "mtime": mtime,
            "step_index": step.get("step_index"),
            "file_path": str(file_path)
        }

    def evaluate_all(self, idle_buffer: int = DEFAULT_IDLE_BUFFER_SECONDS) -> Dict[str, Any]:
        """Evaluates all transcripts found in the brain directory within window_hours."""
        now = time.time()
        max_age = self.window_hours * 3600.0
        files = self.scan_transcripts()
        sessions = []

        for p in files:
            try:
                mtime = os.path.getmtime(p)
            except OSError:
                continue

            if (now - mtime) > max_age:
                continue
            if self.filter_since_start and mtime < self.start_timestamp:
                continue

            sessions.append(self.evaluate_session(p, idle_buffer=idle_buffer))

        # Check for any busy or in-flight sessions
        active_sessions = [s for s in sessions if s["status"] in ("BUSY", "IN_FLIGHT", "SETTLING")]
        waiting_sessions = [s for s in sessions if s["status"] == "WAITING_USER"]
        all_completed = (len(active_sessions) == 0 and len(waiting_sessions) == 0)

        summary = f"Total: {len(sessions)} | Active: {len(active_sessions)} | Waiting: {len(waiting_sessions)}"
        return {
            "all_completed": all_completed,
            "active_count": len(active_sessions),
            "subagent_count": len(active_sessions),
            "waiting_count": len(waiting_sessions),
            "sessions": sessions,
            "summary": summary
        }
