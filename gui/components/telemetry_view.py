# -*- coding: utf-8 -*-
"""
gui.components.telemetry_view: Tab 2 Real-Time Telemetry Deck Component.
Hosts 4 hardware telemetry cards with embedded waveform sparklines and responsive 2x2 layout.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 300 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Dict, Any, Tuple

from gui.theme import (
    BG_BASE,
    BG_SURFACE,
    BG_SUBSURFACE,
    BORDER_MUTED,
    ACCENT_CYAN,
    STATUS_EMERALD,
    STATUS_AMBER,
    STATUS_SLATE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    FONT_SUBHEADER,
    FONT_BODY,
    FONT_BADGE,
)
from gui.components.sparklines import CanvasSparkline
from gui.components.status_resolver import resolve_input_activity_state


class TelemetryView(tk.Frame):
    """
    Tab 2 Telemetry View Component:
    Displays 4 distinct translucent cards with embedded real-time sparklines:
      1. CPU Activity & Load (Emerald single-trace sparkline)
      2. Network Throughput & I/O (Cyan / Indigo dual-trace sparkline)
      3. Antigravity AI Monitor (Active PIDs, workers, memory footprint)
      4. User Input & WASAPI Audio (Physical idle clock & audio state)
    """

    def __init__(self, parent: tk.Widget, **kwargs: Any):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.is_studio_view = True
        self.cpu_peak = 0.0
        self._last_telemetry: Dict[str, Any] = {}

        self._build_cards()
        self.set_studio_view(True)

    def _build_cards(self) -> None:
        """Construct all 4 telemetry cards and link backward compatibility aliases."""
        self._build_cpu_card()
        self._build_net_card()
        self._build_ai_card()
        self._build_input_card()
        self._link_legacy_aliases()

    def _build_cpu_card(self) -> None:
        """Construct Card 1: CPU Activity & Load with single-trace sparkline."""
        self.card_cpu, self.lbl_cpu_metrics, self.pill_cpu = self._create_card_container(
            title="⚡ CPU Activity & Load",
            initial_pill=" SAFE ",
            pill_color=STATUS_EMERALD,
            initial_metric="Current: 0.0% | Peak: 0.0% | Limit: 15.0%",
        )
        self.spark_cpu = CanvasSparkline(
            self.card_cpu, width=180, height=36, bg=BG_SUBSURFACE,
            line_color=STATUS_EMERALD, fill_color="#0d2e26",
        )
        self.spark_cpu.pack(fill="x", expand=True, pady=(4, 2))

    def _build_net_card(self) -> None:
        """Construct Card 2: Network Throughput & I/O with dual-trace sparkline."""
        self.card_net, self.lbl_net_metrics, self.pill_net = self._create_card_container(
            title="🌐 Network Throughput & I/O",
            initial_pill=" IDLE ",
            pill_color=STATUS_SLATE,
            initial_metric="↓ 0.0 KB/s  ↑ 0.0 KB/s",
        )
        self.spark_net = CanvasSparkline(
            self.card_net, width=180, height=36, bg=BG_SUBSURFACE,
            line_color=ACCENT_CYAN, fill_color="#082a36",
            line_color2="#6366F1", fill_color2="#1e1b4b",
        )
        self.spark_net.pack(fill="x", expand=True, pady=(4, 2))

    def _build_ai_card(self) -> None:
        """Construct Card 3: Antigravity AI Monitor status card."""
        self.card_ai, self.lbl_ai_metrics, self.pill_ai = self._create_card_container(
            title="🤖 Antigravity AI Monitor",
            initial_pill=" READY ",
            pill_color=STATUS_EMERALD,
            initial_metric="Active PIDs: 0 | Workers: 0 | RAM: 0 MB",
        )
        self.lbl_ai_sub = tk.Label(
            self.card_ai, text="AI Engine: Monitored Subagent Tasks",
            font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_SURFACE,
        )
        self.lbl_ai_sub.pack(anchor="w", pady=(2, 0))

    def _build_input_card(self) -> None:
        """Construct Card 4: User Input & WASAPI Audio status card."""
        self.card_input, self.lbl_input_metrics, self.pill_input = self._create_card_container(
            title="🎙️ Input & WASAPI Audio",
            initial_pill=" IDLE ",
            pill_color=STATUS_SLATE,
            initial_metric="0.0s / 60s | Audio: Silent",
        )
        self.lbl_input_sub = tk.Label(
            self.card_input, text="Physical Input Hook & WASAPI Endpoint",
            font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_SURFACE,
        )
        self.lbl_input_sub.pack(anchor="w", pady=(2, 0))

    def _link_legacy_aliases(self) -> None:
        """Preserve legacy attribute aliases for existing unit tests."""
        self.card_l1, self.lbl_l1_val, self.pill_l1 = self.card_input, self.lbl_input_metrics, self.pill_input
        self.card_l2, self.lbl_l2_val, self.pill_l2 = self.card_ai, self.lbl_ai_metrics, self.pill_ai
        self.card_l3, self.lbl_l3_val, self.pill_l3 = self.card_cpu, self.lbl_cpu_metrics, self.pill_cpu
        self.card_l4, self.lbl_l4_val, self.pill_l4 = self.card_net, self.lbl_net_metrics, self.pill_net

    def _create_card_container(
        self, title: str, initial_pill: str, pill_color: str, initial_metric: str
    ) -> Tuple[tk.Frame, tk.Label, tk.Label]:
        """Create a translucent card with title header, status badge, and metric label."""
        card = tk.Frame(
            self, bg=BG_SURFACE, highlightbackground=BORDER_MUTED,
            highlightthickness=1, padx=10, pady=8,
        )
        hdr = tk.Frame(card, bg=BG_SURFACE)
        hdr.pack(fill="x", anchor="w")
        tk.Label(
            hdr, text=title, font=FONT_SUBHEADER, fg=TEXT_PRIMARY, bg=BG_SURFACE
        ).pack(side="left")
        pill = tk.Label(
            hdr, text=f" {initial_pill.strip()} ", font=FONT_BADGE,
            fg=TEXT_PRIMARY, bg=pill_color, padx=6, pady=1,
        )
        pill.pack(side="right")
        lbl_metric = tk.Label(
            card, text=initial_metric, font=FONT_BODY,
            fg=TEXT_SECONDARY, bg=BG_SURFACE, anchor="w",
        )
        lbl_metric.pack(fill="x", pady=(4, 0))
        return card, lbl_metric, pill

    def set_studio_view(self, is_studio: bool) -> None:
        """Switch between 4-card vertical stack (compact) and 2x2 grid (studio)."""
        self.is_studio_view = is_studio
        for card in (self.card_cpu, self.card_net, self.card_ai, self.card_input):
            card.pack_forget()
            card.grid_forget()

        if not is_studio:
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=0)
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            for card in (self.card_cpu, self.card_net, self.card_ai, self.card_input):
                card.pack(fill="x", padx=4, pady=3)
            return

        self.grid_columnconfigure(0, weight=1, uniform="card_col")
        self.grid_columnconfigure(1, weight=1, uniform="card_col")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.card_cpu.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self.card_net.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self.card_ai.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        self.card_input.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")

    def _merge_telemetry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge incoming partial telemetry payload into retained baseline snapshot."""
        self._last_telemetry.update(data)
        if "subagent_count" in data and "worker_count" not in data:
            self._last_telemetry["worker_count"] = data["subagent_count"]
        elif "workers" in data and "worker_count" not in data:
            self._last_telemetry["worker_count"] = data["workers"]
        return self._last_telemetry

    def _update_cpu_card(self, merged: Dict[str, Any], raw: Dict[str, Any]) -> None:
        """Update CPU metrics, threshold pill, and single-trace sparkline."""
        cpu_val = float(merged.get("cpu_percent", merged.get("cpu_pct", 0.0)))
        self.cpu_peak = max(self.cpu_peak, cpu_val)
        cpu_limit = float(merged.get("cpu_threshold", merged.get("cpu_limit", 15.0)))
        if "cpu_percent" in raw or "cpu_pct" in raw:
            self.spark_cpu.push_value(cpu_val, max_val=100.0)
        self.lbl_cpu_metrics.config(
            text=f"Current: {cpu_val:.1f}% | Peak: {self.cpu_peak:.1f}% | Limit: {cpu_limit:.1f}%"
        )
        if cpu_val >= cpu_limit:
            self.pill_cpu.config(text=" HIGH ", bg=STATUS_AMBER)
        else:
            self.pill_cpu.config(text=" SAFE ", bg=STATUS_EMERALD)

    def _update_net_card(self, merged: Dict[str, Any], raw: Dict[str, Any]) -> None:
        """Update Network metrics, threshold pill, and dual-trace sparkline."""
        rx_kb = float(merged.get("net_rx_kbps", merged.get("download_kb", merged.get("net_download_kb", 0.0))))
        tx_kb = float(merged.get("net_tx_kbps", merged.get("upload_kb", merged.get("net_upload_kb", 0.0))))
        net_thresh = float(merged.get("net_threshold", 50.0))
        net_total = float(merged.get("net_total_kb", rx_kb + tx_kb))
        if any(k in raw for k in ("net_rx_kbps", "download_kb", "net_download_kb", "net_tx_kbps", "upload_kb", "net_upload_kb")):
            self.spark_net.push_dual_values(rx_kb, tx_kb, max_val=max(100.0, rx_kb, tx_kb))
        self.lbl_net_metrics.config(text=f"↓ {rx_kb:.1f} KB/s  ↑ {tx_kb:.1f} KB/s")
        if net_total >= net_thresh and (net_total > 0.0 or net_thresh > 0.0):
            self.pill_net.config(text=" ACTIVE ", bg=ACCENT_CYAN)
        else:
            self.pill_net.config(text=" IDLE ", bg=STATUS_SLATE)

    def _update_ai_card(self, merged: Dict[str, Any]) -> None:
        """Update Antigravity AI Monitor PID, worker, and memory metrics."""
        pids = merged.get("active_pids", merged.get("monitored_pids", []))
        pids_count = len(pids) if isinstance(pids, list) else int(merged.get("active_sessions_count", 0))
        raw_workers = merged.get("worker_count", merged.get("workers", merged.get("subagent_count", 0)))
        workers = int(0 if raw_workers is None else raw_workers)
        mem = merged.get("memory_mb", merged.get("ai_memory", 0))
        self.lbl_ai_metrics.config(
            text=f"Active PIDs: {pids_count} | Workers: {workers} | RAM: {mem} MB"
        )
        is_ai_busy = bool(workers > 0 or pids_count > 0 or merged.get("is_tree_busy", False))
        if is_ai_busy:
            self.pill_ai.config(text=" WORKING ", bg=ACCENT_CYAN)
        else:
            self.pill_ai.config(text=" READY ", bg=STATUS_EMERALD)

    def _update_input_card(self, merged: Dict[str, Any]) -> None:
        """Update physical user inactivity and WASAPI audio telemetry."""
        raw_idle = merged.get("idle_sec", merged.get("user_inactivity_sec"))
        raw_thresh = merged.get("idle_threshold", merged.get("inactivity_threshold_sec"))
        idle_sec = float(0.0 if raw_idle is None else raw_idle)
        idle_threshold = float(60.0 if raw_thresh is None else raw_thresh)
        audio_active = bool(merged.get("audio_active", False))
        audio_desc = "Active [Inhibit]" if audio_active else "Silent"
        self.lbl_input_metrics.config(
            text=f"{idle_sec:.1f}s / {idle_threshold:.0f}s | Audio: {audio_desc}"
        )
        status = resolve_input_activity_state(
            state_name=merged.get("state"),
            idle_sec=None if raw_idle is None else idle_sec,
            idle_threshold=idle_threshold,
            audio_active=audio_active,
            has_user_input=merged.get("has_user_input"),
        )
        pill_bg = STATUS_EMERALD if status in ("AWAY", "ACTIVE") else (STATUS_AMBER if status == "AUDIO" else STATUS_SLATE)
        self.pill_input.config(text=f" {status} ", bg=pill_bg)

    def update_telemetry(self, data: Dict[str, Any]) -> None:
        """Update metrics, badges, and sparklines across all 4 telemetry cards."""
        if not data:
            return
        merged = self._merge_telemetry(data)
        self._update_cpu_card(merged, data)
        self._update_net_card(merged, data)
        self._update_ai_card(merged)
        self._update_input_card(merged)
