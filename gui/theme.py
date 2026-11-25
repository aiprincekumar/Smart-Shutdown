# -*- coding: utf-8 -*-
"""
gui.theme: Windows 11 Fluent Dark Design System tokens and UI styling utilities.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

# Surface and Background Color Tokens (Fluent Dark per DESIGN.md)
BG_BASE = "#12141A"          # Deep Obsidian Slate - Root window canvas background
BG_SURFACE = "#181B22"       # Card, container, and toolbar background
BG_SUBSURFACE = "#222631"    # Secondary nested surface / slider troughs / inactive tab pills
BG_HOVER = "#2A303D"         # Interactive hover state for buttons and pills
BORDER_COLOR = "#2E3444"     # Subtle 1px structural container borders
BORDER_MUTED = "#2E3444"     # Subtle 1px structural container borders
BORDER_CYAN_GLOW = "#06B6D4" # Active glowing cyan accent border (1px)
BORDER_FOCUS = "#06B6D4"     # Focused element accent border

# Centralized Futuristic Mockup Alignment Tokens
TRACK_RING = "#1E2430"
BORDER_CARD = "#1E2B3E"
BORDER_CARD_HOVER = "#2E3F57"
HALO_CYAN = "#083344"
HALO_AMBER = "#3D2610"
HALO_CRIMSON = "#3D1418"

# 2x3 Action Pill Grid Button Tokens
BG_BUTTON_SLATE = "#1B2434"
BORDER_BUTTON_SLATE = "#2A384D"
BG_BUTTON_ABORT = "#221C18"
BORDER_BUTTON_ABORT = "#D97706"
TEXT_BUTTON_ABORT = "#F59E0B"
BG_BUTTON_BYPASS = "#12242D"
BORDER_BUTTON_BYPASS = "#06B6D4"
TEXT_BUTTON_BYPASS = "#00E5FF"
BG_BUTTON_SHUTDOWN = "#2D1418"
BORDER_BUTTON_SHUTDOWN = "#EF4444"
TEXT_BUTTON_SHUTDOWN = "#FF3B30"

# Eligibility and Warning Banner Tokens
BG_BANNER_ELIGIBLE = "#0D241E"
BORDER_BANNER_ELIGIBLE = "#00FF85"
BG_BANNER_INHIBITED = "#261C14"

# Typography Color Tokens
TEXT_PRIMARY = "#F8FAFC"     # High-contrast heading text (WCAG AAA 14:1)
TEXT_SECONDARY = "#94A3B8"   # Subtle descriptions, labels, and timestamps
TEXT_MUTED = "#64748B"       # Helper captions, placeholder text

# Interactive and Brand Accent Tokens
ACCENT_CYAN = "#06B6D4"      # Primary brand accent, progress arcs, active tabs
ACCENT_PURPLE = "#8B5CF6"    # Vibrant Purple Glow - [ 💬 Input ] AI status pill and Settings active
ACCENT_BLUE = "#06B6D4"      # Windows Fluent Blue / Cyan accent
ACCENT_HOVER = "#2A303D"     # Hover and active button states
ACCENT_DARK = "#005A9E"      # Pressed button state
WARN_COLOR = "#F59E0B"       # Warning amber

# Semantic Status Tokens
STATUS_EMERALD = "#10B981"   # Emerald Green Glow - [ ⏱️ Running ] Sentinel pill and countdown health
STATUS_GREEN = "#10B981"     # Active, ready, tasks completed
STATUS_AMBER = "#F59E0B"     # Amber Warning - [ ⏸️ Paused ] pill and countdown < 60s warning
STATUS_CRIMSON = "#EF4444"   # Crimson Red - [ 🛑 Blocked ], [ ⚡ Shutdown Now ] primary button
STATUS_RED = "#EF4444"       # Grace window, app close, critical shutdown
STATUS_ORANGE = "#F97316"    # [ ⏳ Grace ] pill state
STATUS_SLATE = "#64748B"     # Inactive status pills, disabled chips, subtitle text
STATUS_GRAY = "#64748B"      # Disarmed, idle, disconnected

# Terminal Tokens
TERMINAL_BG = "#12141A"      # Console background
TERMINAL_TEXT = "#E0E0E0"    # Standard console text

# Typography Font Tokens
FONT_FAMILY = "Segoe UI Variable Text"
FONT_FAMILY_DISPLAY = "Segoe UI Variable Display"
FONT_FAMILY_MONO = "Consolas"

FONT_TITLE = (FONT_FAMILY_DISPLAY, 11, "bold")     # Header title and branding
FONT_CLOCK = (FONT_FAMILY_DISPLAY, 32, "bold")     # Circular countdown gauge
FONT_HEADER = (FONT_FAMILY, 10, "bold")            # Card headings and section titles
FONT_SUBHEADER = (FONT_FAMILY, 9, "bold")          # Health summary labels
FONT_HEALTH_HEADER = (FONT_FAMILY, 12, "bold")     # Informative Live Health Summary title
FONT_BODY = (FONT_FAMILY, 9, "normal")             # Standard body, buttons, chips
FONT_BODY_BOLD = (FONT_FAMILY, 9, "bold")          # Action buttons, active tabs
FONT_BADGE = (FONT_FAMILY, 8, "bold")              # Status pills, mode switcher
FONT_ICONS = ("Segoe UI Symbol", 10, "normal")     # Title bar and toolbar glyphs
FONT_CONSOLE = (FONT_FAMILY_MONO, 9, "normal")     # Terminal log entries
FONT_TERMINAL = (FONT_FAMILY_MONO, 8, "normal")
