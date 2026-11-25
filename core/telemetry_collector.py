# -*- coding: utf-8 -*-
"""
core.telemetry_collector: Non-blocking hardware, network, audio, and process tree telemetry collector.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import time
from typing import Dict, Any, Tuple, Optional
import psutil

from core.config import SettingsConfig
import core.audio as core_audio
import core.process_tree as process_tree


class TelemetryCollector:
    """Stateful collector for real-time CPU, network delta, WASAPI audio, and worker PID telemetry."""

    def __init__(self) -> None:
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass
        try:
            self._prev_net = psutil.net_io_counters()
        except Exception:
            self._prev_net = None
        self._prev_ts: float = time.monotonic()
        self._last_rx_kbps: float = 0.0
        self._last_tx_kbps: float = 0.0
        self._last_total_kb: float = 0.0

    def _sample_cpu(self) -> float:
        """Read non-blocking system-wide CPU utilization percentage."""
        try:
            val = psutil.cpu_percent(interval=None)
            return max(0.0, round(float(val or 0.0), 1))
        except Exception:
            return 0.0

    def _sample_network(self) -> Tuple[float, float, float]:
        """Compute RX/TX KB/s and combined KB/s over elapsed dt >= 0.2s."""
        now = time.monotonic()
        try:
            curr = psutil.net_io_counters()
        except Exception:
            curr = None

        if curr is None:
            return self._last_rx_kbps, self._last_tx_kbps, self._last_total_kb

        if self._prev_net is None:
            self._prev_net = curr
            self._prev_ts = now
            return 0.0, 0.0, 0.0

        dt = now - self._prev_ts
        if dt < 0.2:
            return self._last_rx_kbps, self._last_tx_kbps, self._last_total_kb

        rx_bytes = max(0, int(getattr(curr, "bytes_recv", 0)) - int(getattr(self._prev_net, "bytes_recv", 0)))
        tx_bytes = max(0, int(getattr(curr, "bytes_sent", 0)) - int(getattr(self._prev_net, "bytes_sent", 0)))
        rx_kbps = max(0.0, round((rx_bytes / 1024.0) / dt, 1))
        tx_kbps = max(0.0, round((tx_bytes / 1024.0) / dt, 1))
        total_kb = max(0.0, round(rx_kbps + tx_kbps, 1))

        self._prev_net = curr
        self._prev_ts = now
        self._last_rx_kbps, self._last_tx_kbps, self._last_total_kb = rx_kbps, tx_kbps, total_kb
        return rx_kbps, tx_kbps, total_kb

    def _sample_process_tree(self) -> Dict[str, Any]:
        """Query non-blocking descendant worker telemetry safely."""
        try:
            res = process_tree.get_process_tree_telemetry()
            if isinstance(res, dict):
                return res
        except Exception:
            pass
        return {"active_pids": [], "worker_count": 0, "memory_mb": 0, "is_tree_busy": False}

    def _sample_audio(self, audio_inhibit_enabled: bool) -> bool:
        """Query WASAPI playback activity only when audio inhibition is enabled."""
        if not audio_inhibit_enabled:
            return False
        try:
            return bool(core_audio.is_audio_stream_active())
        except Exception:
            return False

    def sample(self, config: SettingsConfig) -> Dict[str, Any]:
        """Collect one unified snapshot of hardware, network, audio, and process-tree telemetry."""
        cpu_percent = self._sample_cpu()
        net_rx_kbps, net_tx_kbps, net_total_kb = self._sample_network()
        tree = self._sample_process_tree()
        audio_enabled = bool(getattr(config, "audio_inhibit_enabled", True))
        audio_active = self._sample_audio(audio_enabled)

        return {
            "cpu_percent": cpu_percent,
            "cpu_threshold": float(getattr(config, "cpu_threshold_pct", 15.0)),
            "net_rx_kbps": net_rx_kbps,
            "net_tx_kbps": net_tx_kbps,
            "net_total_kb": net_total_kb,
            "net_threshold": float(getattr(config, "network_threshold_kb", 50.0)),
            "audio_active": audio_active,
            "audio_inhibit_enabled": audio_enabled,
            "active_pids": list(tree.get("active_pids", [])),
            "worker_count": int(tree.get("worker_count", 0)),
            "memory_mb": int(tree.get("memory_mb", 0)),
            "is_tree_busy": bool(tree.get("is_tree_busy", False)),
        }


def evaluate_hardware_block(hw: Dict[str, Any], config: SettingsConfig) -> Optional[str]:
    """Return inhibition reason ('audio_active' or 'hardware_busy') if limits are exceeded."""
    if not hw:
        return None
    if bool(hw.get("audio_active", False)) and bool(getattr(config, "audio_inhibit_enabled", True)):
        return "audio_active"
    cpu_pct = float(hw.get("cpu_percent", 0.0) or 0.0)
    net_kb = float(hw.get("net_total_kb", 0.0) or 0.0)
    cpu_thresh = float(getattr(config, "cpu_threshold_pct", 15.0))
    net_thresh = float(getattr(config, "network_threshold_kb", 50.0))
    if cpu_pct >= cpu_thresh or (net_kb >= net_thresh and (net_kb > 0.0 or net_thresh > 0.0)):
        return "hardware_busy"
    return None


__all__ = ["TelemetryCollector", "evaluate_hardware_block"]
