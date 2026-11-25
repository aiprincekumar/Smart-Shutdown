# -*- coding: utf-8 -*-
"""
gui.components.title_bar: Modular custom title bar component with sequential cluster.
Branding, AI Status Pill, Sentinel Status Pill, Mode Switcher, and Icon-Only Controls.
Department 05 Frontend and Desktop Engineering.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import tkinter as tk
from enum import Enum
from typing import Optional, Callable, Union

from gui.theme import (
    BG_SURFACE, BG_SUBSURFACE, BG_HOVER, BORDER_MUTED, BORDER_CARD, TEXT_PRIMARY,
    TEXT_SECONDARY, ACCENT_CYAN, ACCENT_PURPLE, STATUS_EMERALD, STATUS_AMBER,
    STATUS_CRIMSON, STATUS_SLATE, STATUS_ORANGE, FONT_TITLE, FONT_BADGE, FONT_ICONS,
)
from gui.components.status_formatter import TelemetryTooltip


class AntiGravityAIState(str, Enum):
    """Priority-driven status of AntiGravity AI engine."""
    INPUT_PENDING = "WAITING"     # [ 💬 Waiting ]
    WORKING = "WORKING"           # [ ⚙️ Working ]
    BUSY = "BUSY"                 # [ 🤖 AI Busy ] (backward-compatible alias)
    READY = "READY"               # [ ✨ Ready ]


class SentinelState(str, Enum):
    """Operational lifecycle state of Sentinel power daemon."""
    IDLE_MONITORING = "IDLE"                      # [ 💤 Idle ]
    ABORTED_RESET = "IDLE"                        # [ 💤 Idle ] (alias)
    RUNNING = "RUNNING"                           # [ ⏱️ Running ]
    COUNTDOWN_ACTIVE = "RUNNING"                  # backward-compatible alias
    AWAY = "AWAY"                                 # [ 👤 Away ]
    ACTIVE = "ACTIVE"                             # [ 🟢 Active ]
    AI_EVALUATION = "AI_EVALUATION"               # [ 🔍 Evaluating ]
    WAITING_USER_PROMPT = "WAITING_USER_PROMPT"   # [ 💬 Waiting ]
    PAUSED = "PAUSED"                             # [ ⏸️ Paused ]
    CLOSING = "CLOSING"                           # [ 🚪 Closing ]
    PRE_SHUTDOWN_GRACE = "CLOSING"                # backward-compatible alias
    SHUTDOWN_EXECUTED = "SHUTDOWN"                # [ ⚡ Shutdown ]
    BLOCKED = "BLOCKED"                           # [ 🛑 Blocked ]
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"


from core.models import TargetMode


class TitleBarComponent(tk.Frame):
    """Modular top title bar with sequential status cluster and icon-only controls."""

    MODE_CYCLE = [TargetMode.LIVE, TargetMode.DEMO_30S, TargetMode.SIMULATION]
    MODE_DISPLAY = {
        TargetMode.LIVE: ("[ ⚡ Live ]", STATUS_CRIMSON),
        TargetMode.DEMO_30S: ("[ ⚡ Demo (30s) ]", STATUS_CRIMSON),
        TargetMode.SIMULATION: ("[ 🛡️ Simulation ]", ACCENT_CYAN),
        TargetMode.DEMO_10S: ("[ 🧪 Demo (10s) ]", STATUS_AMBER),
    }

    def __init__(
        self,
        parent: tk.Misc,
        on_mode_change: Optional[Callable[[TargetMode], None]] = None,
        on_detach_hud: Optional[Callable[[], None]] = None,
        on_tray_minimize: Optional[Callable[[], None]] = None,
        on_taskbar_minimize: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent, bg=BG_SURFACE, highlightbackground=BORDER_MUTED,
            highlightthickness=1, padx=6, pady=3, **kwargs
        )
        self.on_mode_change = on_mode_change
        self.on_detach_hud = on_detach_hud
        self.on_tray_minimize = on_tray_minimize
        self.on_taskbar_minimize = on_taskbar_minimize
        self.on_close = on_close

        self.current_mode = TargetMode.LIVE
        self.ai_state = AntiGravityAIState.READY
        self.sentinel_state = SentinelState.IDLE_MONITORING

        self._build_right_cluster()
        self._build_left_cluster()

    def _build_right_cluster(self) -> None:
        """Construct strictly icon-only window control buttons (pinned to right)."""
        right = tk.Frame(self, bg=BG_SURFACE)
        right.pack(side="right", fill="y")

        self.btn_hud = self._create_icon_btn(
            right, text="📌", tooltip="Detach Floating Mini HUD",
            command=lambda: self.on_detach_hud() if self.on_detach_hud else None
        )
        # Windows 11 caret glyph '\uFE3D' (︿), strictly NOT a download arrow
        self.btn_tray = self._create_icon_btn(
            right, text="︿", tooltip="Send to System Tray",
            command=lambda: self.on_tray_minimize() if self.on_tray_minimize else None
        )
        self.btn_min = self._create_icon_btn(
            right, text="—", tooltip="Minimize to Taskbar",
            command=lambda: self.on_taskbar_minimize() if self.on_taskbar_minimize else None
        )
        self.btn_close = self._create_icon_btn(
            right, text="✕", tooltip="Close to System Tray",
            command=lambda: self.on_close() if self.on_close else None, is_close=True
        )

        for btn in (self.btn_hud, self.btn_tray, self.btn_min, self.btn_close):
            btn.pack(side="left", padx=1)

    def _build_left_cluster(self) -> None:
        """Construct sequential left cluster: Branding -> AI Pill -> Sentinel Pill -> Mode Switcher."""
        left = tk.Frame(self, bg=BG_SURFACE)
        left.pack(side="left", fill="both", expand=True)

        # 1. Branding: Shield icon + Smart Shutdown
        self.lbl_branding = tk.Label(
            left, text="🛡️ Smart Shutdown", font=FONT_TITLE, fg=TEXT_PRIMARY, bg=BG_SURFACE
        )
        self.lbl_branding.pack(side="left", padx=(0, 6))

        # 2. Priority AntiGravity AI Status Pill (Default: [ ✨ Ready ])
        self.pill_ai = tk.Label(
            left, text="[ ✨ Ready ]", font=FONT_BADGE, fg=STATUS_SLATE, bg=BG_SUBSURFACE,
            relief="solid", bd=1, highlightthickness=1, highlightbackground=BORDER_CARD, padx=6, pady=2
        )
        self.pill_ai.pack(side="left", padx=3)

        # 3. Sentinel Status Pill (Default: [ 💤 Idle ])
        self.pill_sentinel = tk.Label(
            left, text="[ 💤 Idle ]", font=FONT_BADGE, fg=STATUS_SLATE, bg=BG_SUBSURFACE,
            relief="solid", bd=1, highlightthickness=1, highlightbackground=BORDER_CARD, padx=6, pady=2
        )
        self.pill_sentinel.pack(side="left", padx=3)

        # 4. Dynamic Mode Switcher (Default: [ ⚡ Live ])
        self.btn_mode = tk.Button(
            left, text="[ ⚡ Live ]", font=FONT_BADGE, fg=STATUS_CRIMSON, bg="#2D1418",
            activebackground="#3D1418", activeforeground="#FF3B30", relief="flat", bd=0,
            highlightthickness=1, highlightbackground=STATUS_CRIMSON, padx=6, pady=2, cursor="hand2",
            command=self._cycle_mode
        )
        self.btn_mode.pack(side="left", padx=3)

    def _create_icon_btn(
        self, parent: tk.Frame, text: str, tooltip: str, command: Callable[[], None], is_close: bool = False
    ) -> tk.Button:
        """Helper to create strictly icon-only button with hover effect and tooltip binding."""
        btn = tk.Button(
            parent, text=text, command=command, font=FONT_ICONS, bg=BG_SURFACE, fg=TEXT_SECONDARY,
            activebackground=STATUS_CRIMSON if is_close else BG_HOVER, activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0, highlightthickness=0, cursor="hand2", width=2, padx=1, pady=1
        )
        btn.tooltip = tooltip
        btn._tooltip_handler = TelemetryTooltip(btn, lambda b=btn: getattr(b, "tooltip", ""))
        if is_close:
            btn.bind("<Enter>", lambda _e: btn.config(bg=STATUS_CRIMSON, fg=TEXT_PRIMARY), add="+")
            btn.bind("<Leave>", lambda _e: btn.config(bg=BG_SURFACE, fg=TEXT_SECONDARY), add="+")
        else:
            btn.bind("<Enter>", lambda _e: btn.config(bg=BG_HOVER, fg=TEXT_PRIMARY), add="+")
            btn.bind("<Leave>", lambda _e: btn.config(bg=BG_SURFACE, fg=TEXT_SECONDARY), add="+")
        return btn

    def set_ai_state(self, state: Optional[Union[AntiGravityAIState, str]]) -> None:
        """Update AntiGravity AI Status Pill."""
        raw = "" if state is None else str(state)
        val = (state.value if isinstance(state, AntiGravityAIState) else raw).strip().upper()
        if "WAITING" in val or "INPUT" in val or "💬" in raw:
            self.ai_state = AntiGravityAIState.INPUT_PENDING
            text, fg, hl, bg = "[ 💬 Waiting ]", ACCENT_PURPLE, ACCENT_PURPLE, "#1E162E"
        elif "BUSY" in val or "🤖" in raw:
            self.ai_state = AntiGravityAIState.BUSY
            text, fg, hl, bg = "[ 🤖 AI Busy ]", ACCENT_CYAN, ACCENT_CYAN, "#083344"
        elif "WORK" in val or "⚙" in raw:
            self.ai_state = AntiGravityAIState.WORKING
            text, fg, hl, bg = "[ ⚙️ Working ]", ACCENT_CYAN, ACCENT_CYAN, "#083344"
        else:
            self.ai_state = AntiGravityAIState.READY
            text, fg, hl, bg = "[ ✨ Ready ]", STATUS_SLATE, BORDER_CARD, BG_SUBSURFACE
        self.pill_ai.config(text=text, fg=fg, highlightbackground=hl, bg=bg)

    _SENTINEL_RULES = (
        (("CLOSING", "GRACE", "CLOSE", "🚪"), SentinelState.CLOSING, "[ 🚪 Closing ]", STATUS_ORANGE, "#2D1C10"),
        (("SHUTDOWN", "⚡"), SentinelState.SHUTDOWN_EXECUTED, "[ ⚡ Shutdown ]", STATUS_CRIMSON, "#2D1418"),
        (("BLOCK", "🛑"), SentinelState.BLOCKED, "[ 🛑 Blocked ]", STATUS_CRIMSON, "#2D1418"),
        (("PAUS", "⏸"), SentinelState.PAUSED, "[ ⏸️ Paused ]", STATUS_AMBER, "#261C14"),
        (("WAITING_USER", "PROMPT", "💬"), SentinelState.WAITING_USER_PROMPT, "[ 💬 Waiting ]", ACCENT_PURPLE, "#1E162E"),
        (("AI_EVAL", "EVAL", "🔍"), SentinelState.AI_EVALUATION, "[ 🔍 Evaluating ]", ACCENT_CYAN, "#083344"),
        (("RUNNING", "COUNTDOWN", "⏱", "⏳"), SentinelState.RUNNING, "[ ⏱️ Running ]", STATUS_EMERALD, "#0D241E"),
        (("AWAY", "👤"), SentinelState.AWAY, "[ 👤 Away ]", STATUS_EMERALD, "#0D241E"),
        (("ACTIVE", "🟢"), SentinelState.ACTIVE, "[ 🟢 Active ]", STATUS_EMERALD, "#0D241E"),
        (("IDLE", "IDLE_MONITORING", "ABORTED_RESET", "💤"), SentinelState.IDLE_MONITORING, "[ 💤 Idle ]", STATUS_SLATE, BG_SUBSURFACE),
    )

    def set_sentinel_state(self, state: Optional[Union[SentinelState, str]]) -> None:
        """Update System Sentinel Status Pill with strict non-colliding precedence."""
        raw = "" if state is None else (state.value if isinstance(state, SentinelState) else str(state))
        val = raw.strip().upper()
        st, text, fg, hl, bg = SentinelState.IDLE_MONITORING, "[ 💤 Idle ]", STATUS_SLATE, BORDER_CARD, BG_SUBSURFACE
        for keys, rule_st, rule_txt, rule_fg, rule_bg in self._SENTINEL_RULES:
            if val == "WAITING" and rule_st == SentinelState.WAITING_USER_PROMPT:
                st, text, fg, hl, bg = rule_st, rule_txt, rule_fg, rule_fg, rule_bg
                break
            if any(k in val or k in raw for k in keys):
                rule_hl = BORDER_CARD if rule_st == SentinelState.IDLE_MONITORING else rule_fg
                st, text, fg, hl, bg = rule_st, rule_txt, rule_fg, rule_hl, rule_bg
                break
        self.sentinel_state = st
        self.pill_sentinel.config(text=text, fg=fg, highlightbackground=hl, bg=bg)

    def _resolve_target_mode(self, mode: Union[TargetMode, str]) -> TargetMode:
        """Normalize TargetMode enum or string into TargetMode."""
        if isinstance(mode, TargetMode):
            return mode
        m_str = str(mode).upper()
        if "30" in m_str or "DEMO" in m_str and "10" not in m_str:
            return TargetMode.DEMO_30S
        if "10" in m_str:
            return TargetMode.DEMO_10S
        if "SIM" in m_str or "DRY" in m_str:
            return TargetMode.SIMULATION
        return TargetMode.LIVE

    def set_mode(self, mode: Union[TargetMode, str], notify: bool = False) -> None:
        """Set execution mode and refresh mode button badge."""
        self.current_mode = self._resolve_target_mode(mode)
        styles = {
            TargetMode.LIVE: ("[ ⚡ Live ]", STATUS_CRIMSON, STATUS_CRIMSON, "#2D1418"),
            TargetMode.DEMO_30S: ("[ ⚡ Demo (30s) ]", STATUS_CRIMSON, STATUS_CRIMSON, "#2D1418"),
            TargetMode.DEMO_10S: ("[ 🧪 Demo (10s) ]", STATUS_AMBER, STATUS_AMBER, "#261C14"),
            TargetMode.SIMULATION: ("[ 🛡️ Simulation ]", ACCENT_CYAN, ACCENT_CYAN, "#083344"),
        }
        label, fg, hl, bg = styles[self.current_mode]
        self.btn_mode.config(
            text=label, fg=fg, activeforeground=fg, highlightbackground=hl, bg=bg,
            activebackground=bg,
        )
        if notify and self.on_mode_change:
            self.on_mode_change(self.current_mode)

    def _cycle_mode(self) -> None:
        """Cycle through Live -> Demo (30s) -> Simulation -> Live."""
        try:
            idx = self.MODE_CYCLE.index(self.current_mode)
            next_mode = self.MODE_CYCLE[(idx + 1) % len(self.MODE_CYCLE)]
        except ValueError:
            next_mode = TargetMode.LIVE
        self.set_mode(next_mode, notify=True)
