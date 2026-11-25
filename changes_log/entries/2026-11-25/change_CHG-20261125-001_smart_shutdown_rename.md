# Detailed Change Entry: CHG-20261125-002

> **Change ID:** `CHG-20261125-002` (File alias: `change_CHG-20261125-001_smart_shutdown_rename.md`)  
> **Timestamp:** `2026-11-25 03:25:00`  
> **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)  
> **Target Scope:** `smart-shutdown-rename-phases-1-to-6a`  
> **Initiative:** `TASK-SMART-SHUTDOWN-RENAME-001`  
> **Authorization Token:** `AUTH-MGR-20261125-SMART-SHUTDOWN-001`  
> **Governing Standards:** Universal Rule 1 (Supreme CEO), Rule 5 & 8 (UTF-8 BOM), Rule 6 (5-Tier Changes Log), Rule 12 (DevOps & Release), Rule 15 (Git Gatekeeper), Rule 16 (Developer Profile), Rule 20 (Diagnostic Matrix), Rule 21 & 23 (Project Memory Dossier), Rule 27 (Rules Health Sentinel), Rule 28 (Code Modularity)

---

## 📋 1. Purpose & Architectural Rationale

Execute a clean, decoupled **Full Product & Application Rename** from **AntiGravity Auto Shutdown Sentinel** (`antigravity-auto-shutdown`) to **Smart Shutdown** (`smart-shutdown` / `smart_shutdown`), eliminating brand confusion between the power-management application and the external Antigravity IDE/AI agent target it monitors:
1. **Phase 1 — Package, Entrypoint, Runtime Config & Startup (`package.json`, `smart_shutdown.py`, `core/config.py`, `core/startup.py`, `core/system_tray.py`):**
   - Updated `package.json` (`"name": "smart-shutdown"`), renamed `antigravity_auto_shutdown.py` -> `smart_shutdown.py`, updated log/lock/settings paths (`smart_shutdown.log`, `smart_shutdown.lock`, `smart_shutdown_settings.json` with legacy `sentinel_settings.json` fallback), logger `"SmartShutdown"`, tray `"Smart Shutdown Cockpit"`, and startup shortcut `Smart_Shutdown.lnk` (with legacy `Antigravity_Auto_Shutdown.lnk` cleanup).
2. **Phase 2 — Core Modules & Rule 28 `core/gui.py` Split (`core/*.py`, `core/gui_widgets.py`):**
   - Updated internal docstrings and `"SmartShutdown"` loggers across `core/`; extracted `core/gui_widgets.py` (131 lines, 7,692 bytes) from `core/gui.py` (compacted from 556 lines / 25,339 bytes to 347 lines / 14,656 bytes with UTF-8 BOM).
   - Preserved 100% of external Antigravity IDE/AI monitoring & process termination targets (`DEFAULT_BRAIN_DIR`, `AntigravitySessionAnalyzer`, `TranscriptSentinel`, `AntiGravityAIState`, `antigravity.exe`, `close_antigravity*`, `ANTIGRAVITY_TEST_MODE`).
3. **Phase 3 — Batch Launchers & Operational Scripts (`Smart_Shutdown.bat`, `launchers/00..09*.bat`, `scripts/*.py`, `scripts/check-rules-health.js`):**
   - Renamed `Antigravity_Auto_Shutdown.bat` -> `Smart_Shutdown.bat`, updated `ENGINE_PATH` / window titles / dual lock cleanup (`smart_shutdown.lock` + `auto_shutdown.lock`), updated script descriptions & UTF-8 BOM, and updated `check-rules-health.js` header banner with `.agents/rules/` MD5 parity intact.
4. **Phase 4 — GUI Branding & Window Titles (`gui/unified_app.py`, `gui/app_event_bridge.py`, `gui/components/*`, `gui/dialogs/*`, `gui/settings_window.py`, `gui/countdown_overlay.py`, `ui_mockup_prompt.md`):**
   - Renamed window titles (`"Smart Shutdown"`, `"Smart Shutdown HUD"`, `"Smart Shutdown Exit"`, `"Smart Shutdown Settings"`), TitleBar branding (`"🛡️ Smart Shutdown"`), and UI copy while preserving `AppEventBridge`, `⚡ HUD` 220x65px layout, and external Antigravity AI telemetry labels.
5. **Phase 5 — Test Suite Synchronization (`tests/__init__.py`, `tests/test_*.py`):**
   - Synchronized imports and branding assertions (`smart_shutdown`, `Smart_Shutdown`, `"🛡️ Smart Shutdown"`).
6. **Step 6A — Memory Sync, 5-Tier Changes Log, CHANGELOG & Outer Folder Lock Check:**
   - Compacted workspace `memory.md` under `< 24 KB` Rule 28 ceiling, synced global `memory.md`, updated `CHANGELOG.md` and 5-tier `changes_log/`, and verified Windows CWD lock on `C:\Users\Atul Verma\Desktop\AntiGravity Auto Shutdown`.

---

## 🛠️ 2. Diagnostic 7-Column Matrix (Universal Rule 20 Compliance)

| S.No | File / Scope | Root Cause | Proposed Fix | Post-Fix Impact | Phase # | Test Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `package.json`, `smart_shutdown.py`, `core/config.py`, `core/startup.py`, `core/system_tray.py` | Package, entrypoint, paths, logger, tray, and Startup `.lnk` used legacy `antigravity-auto-shutdown` identity | Rename to `smart-shutdown`, `smart_shutdown.py`, `SmartShutdown`, `Smart_Shutdown.lnk` with legacy fallback/cleanup | Clean canonical identity & startup continuity | Phase 1 | `python smart_shutdown.py --help` |
| 2 | `core/*.py`, `core/gui.py`, `core/gui_widgets.py` | Legacy logger/docstrings and `core/gui.py` exceeding Rule 28 (`556` lines / `25.3 KB`, no BOM) | Update loggers/docstrings; split `core/gui_widgets.py` (`131` lines) & compact `core/gui.py` (`347` lines / `14.6 KB` + BOM) | Rule 28 & UTF-8 BOM compliance across `core/` | Phase 2 | Core unit tests |
| 3 | `Smart_Shutdown.bat`, `launchers/00..09*.bat`, `scripts/*.py`, `scripts/check-rules-health.js` | Root launcher, batch titles, `ENGINE_PATH`, lock cleanup, and script banners referenced legacy name | Rename root `.bat`, update launchers/scripts + dual lock cleanup + BOM + health banner | Unified 1-click launcher & intact MD5 parity | Phase 3 | `npm run rules:check` |
| 4 | `gui/*`, `ui_mockup_prompt.md` | Desktop window titles, TitleBar branding, dialogs, and copy used `AntiGravity Sentinel` | Rename UI branding to `Smart Shutdown` preserving `AppEventBridge` & AI telemetry labels | Cohesive Smart Shutdown desktop UI & HUD | Phase 4 | GUI & HUD test suites |
| 5 | `tests/__init__.py`, `tests/test_*.py` | Test imports and assertions expected old entrypoint and window branding | Align test imports/assertions to `smart_shutdown` / `Smart Shutdown` | End-to-end rename test alignment | Phase 5 | `unittest discover -s tests` |
| 6 | `memory.md` (local & global), `CHANGELOG.md`, `changes_log/`, outer folder | Local `memory.md` at `31.98 KB` (`> 24 KB`), ledgers stale, outer folder CWD-locked on Windows | Compact local `memory.md` `< 24 KB`, sync global `memory.md` + `CHANGELOG.md` + 5-tier log; verify safe CWD lock | Grade A+ governance readiness & safe folder handoff | Step 6A | Pending Step 6B QA |

---

## 🧪 3. Verification & Pending Step 6B Gate

- **Step 6A Governance Status:** Workspace & global `memory.md` synced (UTF-8 BOM verified), `CHANGELOG.md` and 5-tier `changes_log/` updated, outer folder CWD lock verified non-destructively.
- **Pending Step 6B Independent QA:** Full `python -m unittest discover -s tests -v`, `python smart_shutdown.py --help`, `npm run rules:check`, `gitleaks detect --redact`, ephemeral `temp_prompt/smart_shutdown_rename/` pruning, and Rule 15 local micro-commit.
