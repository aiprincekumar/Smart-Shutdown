﻿# Smart Shutdown - Project Memory Dossier

> **Document Type:** Active Project Working Memory & Architectural State Manifest (Universal Rule 21 & 23)  
> **Project Scope:** Smart Shutdown (`smart-shutdown` / `smart_shutdown`) - Intelligent Windows Power & Inactivity Daemon  
> **Target Path:** [`memory.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/memory.md)  
> **Primary Developer:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)  
> **Constitutional Anchors:** [`foundation_core.md`](file:///.agents/rules/foundation_core.md) | [`architecture_recommendation.md`](file:///.agents/rules/architecture_recommendation.md) | [`dynamic_departments_matrix.md`](file:///.agents/rules/dynamic_departments_matrix.md)

---

## 🚦 0. Live Agent State & Stateful Handoff Ledger (Decision Gate State Machine)

> **Document Type:** Live Dynamic Execution State Machine Ledger  
> **Active Project:** `Smart Shutdown` (Workspace path: `c:\Users\Atul Verma\Desktop\Smart Shutdown`)  
> **Active Task ID:** `TASK-README-ENHANCE-002` (README UI Preview, Troubleshooting FAQ, Contributing & Governance)  
> **Authorization Token:** `AUTH-MGR-20261126-README-ENHANCE-001`  
> **Current Gate State:** `COMPLETED` (`README.md` Enhanced + 5-Tier `changes_log/` + `memory.md` + Local Commit)  
> **Test Status:** `README.md` `< 22 KB` (`BOM=False`/`LF`/Anchors `PASS`) | `rules:check` **22/22** | `gitleaks` **0** | `settings.json` untracked (`1,412` B) | PID `10280` kept  
> **Status:** `COMPLETED` (Committed locally on offline `master`; zero remote push; live daemon `PID 10280`, `smart_shutdown.lock`, `logs/smart_shutdown.log`, and `smart_shutdown_settings.json` preserved)  
> **Sub Manager Heartbeat:** HEALTHY (Continuous Passive Lifecycle Monitor)

### 0.0 Last Completed Milestone: README Enhancement (`TASK-README-ENHANCE-002`)
1. **README Showcase, Troubleshooting, Contributing & Governance (`AUTH-MGR-20261126-README-ENHANCE-001`):**
   - Verified symbols across `scripts/06_cancel_or_exit_monitor.py`, `core/{startup,settings_store}.py`, and `gui/components/{mini_overlay,title_bar,dashboard_view}.py`.
   - Added plain-ASCII ToC/headings for `UI Preview & Visual Layout` (`780x520` cockpit + `220x65` Mini HUD ASCII boxes, `04`/`08`/`09` previews, zero broken images), `Troubleshooting & FAQ` (5-path Python/`--no-pause`, `Smart_Shutdown.lnk` + `reconcile_startup_shortcut`, inhibitors, `06`/`shutdown /a` fallback, `_recover_from_backup`), and `Contributing Guidelines` (Rule 28, `.gitattributes`, `-B`/preview/`rules:check`/`gitleaks` checklist); validated `< 22 KB`, `< 500` lines, `BOM=False`, `LF`, and GitHub-slugger anchors.
   - Updated `memory.md` (`S.No 021`, `< 16 KB`, `BOM=True`, `LF`), 5-tier `changes_log/` (`CHG-20261126-009`), passed pre-commit checks, committed locally, and synced global `memory.md`.

### 0.1 Historical Certified Milestones (Concise Archive)
1. **Public GitHub Polish (`TASK-PUBLIC-GITHUB-POLISH-001`):** Upgraded `README.md` (`18853f2`, `7c6733b`; `33` app targets), tracked `requirements`/`LICENSE`/`.gitattributes`, un-BOMmed `launchers/*.bat`, untracked `smart_shutdown_settings.json`, normalized `LF`s, `CHG-20261126-008`.
2. **Direct GUI & History Reset (`TASK-BAT-DIRECT-GUI-001`, `TASK-GIT-HISTORY-RESET-001`):** Audited `10/10` `launchers/*.bat`, rewrote `Smart_Shutdown.bat` (`BOM=False`, `CRLF`, `--gui`/`FORWARD_ARGS`), reset local history (`631452b` -> `f590b64`), `CHG-20261126-006`/`007`.
3. **Pre-GitHub Cleanup (`TASK-PRE-GITHUB-CLEANUP-001`):** Removed `tests/` (36), `temp_prompt/` (110), `archive/` (3), mocks, `.bak`, caches & old log; hardened `.gitignore`; `CHG-20261126-005`.
4. **Live 15m/60s & Sim 5m/60s (`TASK-LIVE-15M-SIM-5M-60S-001`):** Set `DEFAULT_SIMULATION_SECONDS = 300`, aligned Live `15m`/`60s`, scoped `10s` to Demo, synced `.json`/`.lnk`; **346/346 PASS**, `CHG-20261126-004`.
5. **3-State & Sim Parity (`TASK-STATUS-3STATE-AND-RUNNING-SYNC-001`, `TASK-SIMULATION-1MIN-DEFAULT-001`, `TASK-STATUS-IDLE-DEFAULT-FIX-001`):** Split `RUNNING` vs `Idle`/`Active`/`Away`, `resolve_mode_duration_seconds()`, `has_user_input`; **346/346 PASS**, `CHG-20261126-001`..`003`.
6. **Status Unification & Persistence (`TASK-STATUS-DISPLAY-SYNC-FIX-001`, `TASK-MINI-HUD-SHUTDOWN-PERSISTENCE-001`):** Unified 5 GUI surfaces (`338/338`), `core/settings_store.py` (`fsync`+`.bak`), `mini_hud_on_startup=True`, `reconcile_startup_shortcut` (`337/337`), `CHG-20261125-004`/`005`.
7. **Rename & Audit (`TASK-POST-RENAME-VERIFICATION-001`..`TASK-STARTUP-HUD-001`):** Smart Shutdown rename & `.lnk` (`311/311`), decoupled 6 modules + lazy barrels (`302/302`), `withdraw()` (`273/273`), dual timers (`257/257`), Live default (`226/226`), `CHG-20261125-001`..`003`.

---

## ⚙️ 1. Project Identity, Mission & Runtime Environment

- **Project Name:** Smart Shutdown (`smart-shutdown`)
- **Core Mission:** Autonomous Windows inactivity detection, external Antigravity IDE/AI session analysis, graceful Tkinter countdown warning overlay & Mini HUD, and safe system power management (`shutdown`, `sleep`, `hibernate`, `lock`) for unattended workstations.
- **Runtime Environment:** Windows 10/11 x64 | Python 3.10+ (3.12+ active) | `tkinter`, `psutil>=5.9.0`, `pillow>=10.0.0`; primary Win32 APIs via stdlib `ctypes` (`pywin32>=306` optional fallback); optional `pycaw>=20240210` + `comtypes>=1.2.0` (WASAPI audio) & `pystray>=0.19.0` (tray)
- **Primary Entry Points:** `smart_shutdown.py`, `Smart_Shutdown.bat`
- **Runtime Artifacts:** `logs/smart_shutdown.log`, `smart_shutdown.lock`, `smart_shutdown_settings.json` (gitignored local config), Startup shortcut `Smart_Shutdown.lnk`

---

## 🗺️ 2. Pre-Mapped Directory Topology (Zero-Scan Bootstrap)

```
Smart Shutdown/ (Product: Smart Shutdown)
├── .agents/rules/                      # Mirrored canonical rules (8 core + 14 departments_archive/)
├── core/                               # Modular backend engine & legacy countdown dialog (25 files)
│   ├── __init__.py                     # Package exports & public API
│   ├── analyzer.py                     # External Antigravity session analyzer & idle evaluator
│   ├── app_closer.py                   # Safe multi-tier application closer
│   ├── app_targets.py                  # Critical OS whitelist & user app targets
│   ├── audio.py                        # WASAPI audio endpoint session poller
│   ├── config.py                       # Global paths, logger ("SmartShutdown"), settings persistence
│   ├── console.py                      # Windows console window hiding utility
│   ├── coordinator.py                  # Master state machine & background monitoring loop
│   ├── gui.py                          # Legacy Tkinter countdown window (347 lines, < 24 KB)
│   ├── gui_widgets.py                  # Extracted legacy GUI widget builders (131 lines)
│   ├── input_hook.py                   # Real-time physical keyboard/mouse activity tracker
│   ├── killer.py                       # Graceful & force process termination routines
│   ├── models.py                       # LifecycleState, TargetMode, AntiGravityAIState, TelemetryEvent
│   ├── monitor.py                      # Headless polling & state machine loop
│   ├── monitor_power.py                # Win32 DPMS display power toggle
│   ├── process_tree.py                 # Process tree inspection & descendant safety
│   ├── settings_store.py               # Atomic JSON persistence, fsync, .json.bak recovery
│   ├── shutdown.py                     # Windows shutdown/abort wrapper
│   ├── shutdown_dispatcher.py          # Multi-action power dispatcher (shutdown/sleep/hibernate/lock)
│   ├── startup.py                      # Windows Startup shortcut manager (Smart_Shutdown.lnk)
│   ├── system_tray.py                  # Detached pystray system tray controller
│   ├── telemetry_collector.py          # Live CPU/Net/Disk/Process telemetry collector
│   ├── transcript_sentinel.py          # External Antigravity transcript watcher
│   ├── waiting_gate.py                 # User prompt / subagent waiting gate evaluator
│   └── win32_window.py                 # Win32 window enumeration & graceful close helpers
├── gui/                                # Unified Fluent Dark Tkinter Desktop App & Mini HUD (27 files)
│   ├── __init__.py                     # PEP 562 lazy barrel exports
│   ├── app_event_bridge.py             # Extracted coordinator-to-GUI event bridge
│   ├── countdown_overlay.py            # Pre-shutdown countdown overlay
│   ├── settings_window.py              # Standalone settings window wrapper
│   ├── theme.py                        # Fluent Dark color & font tokens
│   ├── unified_app.py                  # Master window orchestrator (UnifiedSentinelApp)
│   ├── components/                     # 19 UI components & resolvers
│   └── dialogs/                        # __init__.py, close_confirm_dialog.py
├── launchers/                          # 00..09 Windows batch presets (10 files, BOM=False, CRLF)
├── scripts/                            # 00..07 CLI scripts, preview_*.py, check-rules-health.js (11 files)
├── changes_log/                        # 5-Tier forensic audit tracking (daily/entries/master/recent_10/summary)
├── logs/                               # Runtime log outputs (smart_shutdown.log)
├── .gitattributes                      # Git EOL/binary normalization rules (BOM=False, LF)
├── .gitignore                          # Git ignore rules (BOM=False, LF)
├── .gitleaksignore                     # Secret scanner suppression rules (BOM=False, LF)
├── smart_shutdown.py                   # Unified CLI & GUI entrypoint
├── Smart_Shutdown.bat                  # Direct GUI batch launcher (BOM=False, CRLF)
├── smart_shutdown_settings.json        # Persisted runtime settings (gitignored local config)
├── requirements.txt                    # Python dependency manifest (BOM=False, LF)
├── LICENSE                             # MIT License (2026 Atul Verma, BOM=False, LF)
├── README.md                           # Public repository documentation (BOM=False, LF)
├── package.json                        # Node workspace metadata ("smart-shutdown", rules:check)
├── cliff.toml                          # git-cliff changelog configuration
├── CHANGELOG.md                        # Conventional Commits changelog
└── memory.md                           # Active working memory & ecosystem state
```

---

## 🩺 3. Diagnostic Tracking Matrix (Universal Rule 20)

| S.No | Defect / File | Root Cause | Proposed Fix | Post-Fix Impact | Phase # | Test Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | `.agents/rules/` | Governance rules only global | Mirrored 8 core + 14 playbooks | Zero-drift canonical rules | Phase 1 | Parity MD5 (Pass) |
| 002 | `scripts/check-rules-health.js` | No automated rule check | Modular health checker (< 280 lines) | Deterministic npm rule gate | Phase 1 | `npm run rules:check` |
| 003 | `memory.md` | Lacked zero-scan local anchor | Root `memory.md` with topology/state | Instant zero-scan bootstrap | Phase 2 | UTF-8 BOM & Size |
| 004 | `CHANGELOG.md` | Missing UTF-8 BOM | Prepend BOM + `cliff.toml` | Rule 5 & 8 compliance | Phase 3 | BOM Check (Pass) |
| 005 | Legacy `windows_idle_detector` | Unstaged relocated deletions | Cleanly staged deletions | Clean working tree | Phase 3 | `git status` clean |
| 006 | Boot Auto-Startup / Mini-HUD | Shortcut ran legacy CLI | Targeted `--mini-hud` + expand | Topmost Mini HUD on boot | Phases 1-4 | 95 tests PASS |
| 007 | Demo Mode Hang & Banner | 30s grace > 10s demo | 2s grace, 5s reset, decoupled AI | Clean demo completion/reset | Demo Fix | 195 tests PASS |
| 008 | Combined GUI & Core Audit | Monolithic views/closer | Decoupled 6 modules + lazy barrels | Modular architecture | Phases 1-5 | 302/302 PASS |
| 009 | Product Branding & `core/gui.py` | Legacy name & 25.3 KB file | Renamed to Smart Shutdown; split `gui_widgets.py` | Clear identity & Rule 28 | Phases 1-6 | 306/306 PASS |
| 010 | Post-Rename Shortcut & Sync | Stale `.lnk`, 11 Core/GUI drifts | Regenerated `.lnk`, synced 11 files | Lockstep Core/GUI sync | Phases 1-4 | 311/311 PASS |
| 011 | Mini HUD Persistence | Default `False`, non-atomic save | `core/settings_store.py` + `fsync` + `.bak` | Reboot-resilient settings | Phases 1-4 | 337/337 PASS |
| 012 | Active/Away Status Sync | 5s `Idle` flash, hardcoded Away | Unified 5 GUI surfaces, Bugs A-E | Deterministic status parity | Phases 1-4 | 338/338 PASS |
| 013 | Startup Idle Default 3-State | Startup defaulted to `Active` | Emitted `has_user_input`, 3-state sync | Deterministic `Idle` default | QA & Gov | 346/346 PASS |
| 014 | Simulation 1-Min Default | Inherited `15m` Live timer | `simulation_timer_sec` + scoped CLI | Isolated Simulation timer | Phases 1-3 | 346/346 PASS |
| 015 | 3-State & `RUNNING` Sync | `COUNTDOWN_ACTIVE` merged in `AWAY` | Split `RUNNING` vs `Idle`/`Active`/`Away` | Clear countdown vs presence | Phases 1-3 | 346/346 PASS |
| 016 | Live 15m/60s & Sim 5m/60s | Sim `60s` & forced `10s` idle | `DEFAULT_SIMULATION_SECONDS=300`, `60s` idle | Unified Live/Sim defaults | Phases 1-3 | 346/346 PASS |
| 017 | Pre-GitHub Cleanup (`TASK-PRE-GITHUB-CLEANUP-001`) | Tracked `tests/`, `temp_prompt/`, `archive/`, mocks, `.bak`, caches & old log | `git rm` targets, purge caches, harden `.gitignore`, compact `memory.md` | GitHub-ready clean tree; daemon untouched | Cleanup | `rules:check` 22/22, `py_compile`, `gitleaks` 0 |
| 018 | Git History Reset (`TASK-GIT-HISTORY-RESET-001`) | Multi-commit history held old objects | Orphan `clean_root` -> `master`, expire reflogs, `gc --prune=now --aggressive` | Clean single-commit offline `master` | Reset | `rev-list==1`, `rules:check` 22/22, `gitleaks` 0 |
| 019 | `Smart_Shutdown.bat` (`TASK-BAT-DIRECT-GUI-001`) | BOM prefix error, `:menu`/`0..7`, `:end` `pause` | Rewrite `BOM=False`/`CRLF`, `--gui`/`FORWARD_ARGS`, audit 10 launchers | Instant direct GUI & clean CLI exit | Direct GUI | `--help`/`--startup-status` 0, `rules:check` 22/22 |
| 020 | Public Repo Polish (`TASK-PUBLIC-GITHUB-POLISH-001`) | Stale README, missing packaging/EOL rules, tracked local config | Upgrade `README.md`, track `requirements`/`LICENSE`/`.gitattributes`, untrack settings, `LF` EOLs | Public GitHub-ready repo; PID `10280` kept | Polish | `ls-files --eol`, `rules:check` 22/22, `gitleaks` 0 |
| 021 | README Showcase & FAQ (`TASK-README-ENHANCE-002`) | Lacked ASCII UI layout preview, Troubleshooting FAQ, and Contributing guide | Verify code facts; add `UI Preview`, `Troubleshooting & FAQ`, `Contributing`; validate GitHub slugs & `< 22 KB`; log `CHG-20261126-009` | Self-service onboarding, exact anchors & clean docs | Docs | Anchors PASS, `< 22 KB`, `rules:check` 22/22, `gitleaks` 0 |

---

## 🎯 4. Deterministic Verification & Quality Gate Commands

```bash
# 1. Rules Health & Parity Gatekeeper (Universal Rule 27)
npm run rules:check

# 2. CLI Dispatcher Help & Bytecode-Free Syntax/Import Smoke (safe with live daemon)
python -B smart_shutdown.py --help
python -B -m py_compile smart_shutdown.py

# 3. Token-Free Conventional Changelog Generation
git-cliff --unreleased

# 4. Pre-Commit / Pre-Push Secret Leak Audit
gitleaks detect --redact
```
