# Detailed Change Entry: CHG-20261126-007

> **Change ID:** `CHG-20261126-007`  
> **Timestamp:** `2026-11-26 03:07:36`  
> **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)  
> **Target Scope:** `smart-shutdown-bat-direct-gui-and-launchers-audit`  
> **Initiative:** `TASK-BAT-DIRECT-GUI-001`  
> **Authorization Token:** `AUTH-MGR-20261126-BATGUI-001`  
> **Governing Standards:** Universal Rule 1 (Supreme CEO), Rule 5 & 8 (UTF-8 BOM), Rule 6 (5-Tier Changes Log), Rule 12 (DevOps & Release), Rule 15 (Git Gatekeeper), Rule 16 (Developer Profile), Rule 20 (Diagnostic Matrix), Rule 21 & 23 (Project Memory Dossier), Rule 27 (Rules Health Sentinel)

---

## 📋 1. Purpose & Architectural Rationale

Eliminate the legacy interactive menu, post-execution `SW_HIDE` console hang, and UTF-8 BOM batch prefix error in `Smart_Shutdown.bat` while verifying all 10 preset batch wrappers in `launchers/` without modifying `launchers/*.bat` or disrupting live daemon `PID 8736`:
1. **`launchers/` Audit (`00..09`):**
   - Verified all 10 `.bat` files in `launchers/` exist and every referenced `..\scripts\*.py` target exists on disk (10/10 verified, zero edits to `launchers/`).
2. **`Smart_Shutdown.bat` Direct GUI Rewrite (`BOM=False`, `CRLF`, `BareLF=0`):**
   - Started Line 1 cleanly with `@echo off` (no UTF-8 BOM), Line 2 `@chcp 65001 >nul`, `setlocal EnableDelayedExpansion`, and `:: Smart Shutdown - Direct Unified Desktop GUI Launcher`.
   - Preserved `SCRIPT_DIR`, `ENGINE_PATH`, 5-step Python interpreter lookup, `--no-pause` filtering, and missing-Python/missing-engine `[ERROR]` guards.
   - Removed `:menu`, `:opt0..:opt7`, `0..7` routing, and post-execution `:end` `pause`; added direct `FORWARD_ARGS` pass-through or `--gui` default launch and `exit /b !EXIT_CODE!`.
3. **Governance Sync & Local Offline Commit:**
   - Updated workspace `memory.md` (Section `0` + `S.No 019`, `< 16 KB`, `BOM=True`) and 5-tier `changes_log/` (`CHG-20261126-007`, `BOM=True`); preserved `CHANGELOG.md` untouched and kept `git remote -v` empty (offline only).

---

## 🛠️ 2. Diagnostic 7-Column Matrix (Universal Rule 20 Compliance)

| S.No | File / Scope | Root Cause | Proposed Fix | Post-Fix Impact | Phase # | Test Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `launchers/00..09_*.bat` | Needed audit confirming all 10 preset batch wrappers resolve valid `..\scripts\*.py` targets | Read-only audit of all 10 `launchers/*.bat` and `Test-Path` verification of `scripts/*.py` | 10/10 launcher targets verified intact with zero edits to `launchers/` | Audit | 10/10 target scripts `Exists=True` |
| 2 | `Smart_Shutdown.bat` | File carried UTF-8 BOM (`'∩╗┐'` batch error), legacy `:menu`/`0..7`, and post-execution `:end` `pause` hanging after `SW_HIDE` | Rewrite `BOM=False`, `CRLF`, `BareLF=0`; preserve 5-step Python lookup & `--no-pause`; launch `--gui` directly or forward `FORWARD_ARGS` and exit `!EXIT_CODE!` | Instant direct Unified GUI launch on double-click and clean CLI exit codes | Rewrite | `BOM=False`, `CRLF=86`, `BareLF=0`, `--help` & `--startup-status` Exit `0` |
| 3 | `memory.md`, `changes_log/` (`CHG-20261126-007`), global `memory.md` | Governance ledgers required `TASK-BAT-DIRECT-GUI-001` & `S.No 019` synchronization | Update `memory.md` (`< 16 KB`), 5-tier `changes_log/` (`master < 24 KB`), and global `memory.md` (`<= 665` lines, net `<= 0` B) | 100% Rule 6/21/23 & UTF-8 BOM compliance | Gov | `rules:check` 22/22, `gitleaks` 0 leaks, BOM & size verified |

---

## 🧪 3. Verification & Test Gate Proof

- **Byte & Line-Ending Check (`Smart_Shutdown.bat`):** `BOM=False`, `CRLF=86`, `BareLF=0`.
- **Smoke Checks (`PYTHONDONTWRITEBYTECODE=1`):** `cmd /c "Smart_Shutdown.bat --help --no-pause"` (Exit `0`) and `cmd /c "Smart_Shutdown.bat --startup-status --no-pause"` (Exit `0`), zero `__pycache__/` created, live daemon `PID 8736` untouched.
- **Rules Health & Security:** `npm run rules:check` (`22/22` PASS), `gitleaks detect --redact --no-banner` (`0` leaks), UTF-8 BOM & size ceilings verified.