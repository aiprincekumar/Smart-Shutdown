# -*- coding: utf-8 -*-
"""
gui.components.telemetry_cards: 4-Layer redundant telemetry card deck.
Displays real-time hardware, transcript, process tree, and waiting gate telemetry.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from typing import Dict, Any

from gui.theme import (
    BG_SURFACE,
    BG_SUBSURFACE,
    BORDER_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    STATUS_GREEN,
    STATUS_AMBER,
    STATUS_RED,
    STATUS_GRAY,
    FONT_SUBHEADER,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_BADGE,
)


class TelemetryCardsDeck(tk.Frame):
    """Container hosting 4 telemetry cards matching the 4-layer architecture."""

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, bg=parent["bg"], **kwargs)
        self._build_cards()

    def _build_cards(self) -> None:
        """Construct the 4 telemetry cards in a 2x2 or 4x1 grid."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # Layer 1: Hardware Inactivity
        self.card_l1, self.lbl_l1_val, self.pill_l1 = self._create_card(
            col=0, title="L1: Physical Idle", def_val="0s / 60s", def_status="ACTIVE"
        )
        # Layer 2: AI Transcripts
        self.card_l2, self.lbl_l2_val, self.pill_l2 = self._create_card(
            col=1, title="L2: AI Sessions", def_val="0 In-Flight", def_status="IDLE"
        )
        # Layer 3: Process Tree
        self.card_l3, self.lbl_l3_val, self.pill_l3 = self._create_card(
            col=2, title="L3: Process Tree", def_val="0 Workers", def_status="IDLE"
        )
        # Layer 4: Waiting Gate
        self.card_l4, self.lbl_l4_val, self.pill_l4 = self._create_card(
            col=3, title="L4: Waiting Gate", def_val="Hybrid (10m)", def_status="NORMAL"
        )

    def _create_card(self, col: int, title: str, def_val: str, def_status: str):
        """Helper to create a unified telemetry card."""
        frame = tk.Frame(
            self,
            bg=BG_SURFACE,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=10,
            pady=8
        )
        frame.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        # Top row: Title + Status Pill
        top_frame = tk.Frame(frame, bg=BG_SURFACE)
        top_frame.pack(fill="x", anchor="w")

        lbl_title = tk.Label(
            top_frame,
            text=title,
            bg=BG_SURFACE,
            fg=TEXT_SECONDARY,
            font=FONT_BODY_BOLD
        )
        lbl_title.pack(side="left")

        pill = tk.Label(
            top_frame,
            text=f" {def_status} ",
            bg=STATUS_GRAY,
            fg=TEXT_PRIMARY,
            font=FONT_BADGE,
            relief="flat",
            padx=4
        )
        pill.pack(side="right")

        # Value label
        lbl_val = tk.Label(
            frame,
            text=def_val,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            font=FONT_SUBHEADER,
            anchor="w"
        )
        lbl_val.pack(fill="x", pady=(6, 0))

        return frame, lbl_val, pill

    def update_telemetry(self, data: Dict[str, Any]) -> None:
        """Update metrics and badges across all 4 cards."""
        # Layer 1
        idle_sec = data.get("idle_sec", 0)
        threshold = data.get("idle_threshold", 60)
        self.lbl_l1_val.config(text=f"{idle_sec}s / {threshold}s")
        if idle_sec >= threshold:
            self.pill_l1.config(text=" IDLE ", bg=STATUS_GREEN)
        else:
            self.pill_l1.config(text=" ACTIVE ", bg=STATUS_AMBER)

        # Layer 2
        active_count = data.get("active_sessions_count", 0)
        status_l2 = data.get("transcript_status", "DONE")
        self.lbl_l2_val.config(text=f"{active_count} Active ({status_l2})")
        if active_count > 0:
            self.pill_l2.config(text=" BUSY ", bg=STATUS_AMBER)
        else:
            self.pill_l2.config(text=" DONE ", bg=STATUS_GREEN)

        # Layer 3
        is_tree_busy = data.get("is_tree_busy", False)
        tree_count = data.get("worker_count", 0)
        self.lbl_l3_val.config(text=f"{tree_count} Workers")
        if is_tree_busy:
            self.pill_l3.config(text=" BUSY ", bg=STATUS_AMBER)
        else:
            self.pill_l3.config(text=" IDLE ", bg=STATUS_GREEN)

        # Layer 4
        mode = data.get("waiting_mode", "Hybrid")
        gate_blocked = data.get("gate_blocked", False)
        self.lbl_l4_val.config(text=f"Mode: {mode}")
        if gate_blocked:
            self.pill_l4.config(text=" WAITING ", bg=STATUS_RED)
        else:
            self.pill_l4.config(text=" NORMAL ", bg=STATUS_GREEN)
