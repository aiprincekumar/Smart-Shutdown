# Master Changes Log

> **Archive Index:** Entries from `2026-11-01` to `2026-11-24` (`CHG-20261101-001` .. `CHG-20261124-006`) archived in [`master_changes_log_archive_2026-11.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/master/master_changes_log_archive_2026-11.md).

## [CHG-20261126-009] - 2026-11-26 03:43:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-009_03-43-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-009_03-43-00.md)
- **Target Scope:** `readme-ui-preview-troubleshooting-contributing-sync`
- **Summary:** Enhanced `README.md` (`BOM=False`, `LF`, `< 500` lines, `< 22 KB`) after code verification: added `UI Preview & Visual Layout` (`780x520` cockpit + `220x65` Mini HUD ASCII boxes, `04`/`08`/`09` previews), `Troubleshooting & FAQ`, and `Contributing Guidelines`; synced `memory.md` (`< 16 KB`, `S.No 021`), 5-tier logs, and local offline `master` commit (`PID 10280` preserved).
- **Verification:** Anchors/EOL PASS, `py_compile`/`--help` PASS, `rules:check` 22/22, `gitleaks` 0 leaks.

---

## [CHG-20261126-008] - 2026-11-26 03:24:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-008_03-24-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-008_03-24-00.md)
- **Target Scope:** `public-github-polish-readme-eol-and-governance`
- **Summary:** Upgraded `README.md` (`BOM=False`, `LF`, `< 500` lines, `< 16 KB`) with badges, ToC, Mermaid `flowchart TD`, Quick Start, launchers/CLI tables, 5-tab/HUD/Tray guide, and safety docs; finalized `requirements.txt`, `LICENSE`, `.gitattributes`, `.gitignore`, `.gitleaksignore`, un-BOMmed `launchers/*.bat`, untracked `smart_shutdown_settings.json` (`1,412` B kept on disk), normalized `LF` EOLs, updated `memory.md` (`< 16 KB`, `S.No 020`) & 5-tier logs, renormalized Git index, and committed locally (`PID 10280` preserved).
- **Verification:** `git ls-files --eol`, `rules:check` 22/22, `gitleaks` 0 leaks (repo + `--no-git`), `git status` clean.
- **Rollback:** Restore from git.

---

## [CHG-20261126-007] - 2026-11-26 03:07:36
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-007_03-07-36.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-007_03-07-36.md)
- **Target Scope:** `smart-shutdown-bat-direct-gui-and-launchers-audit`
- **Summary:** Verified 10/10 `launchers/*.bat`; rewrote `Smart_Shutdown.bat` (`BOM=False`, `CRLF`, `BareLF=0`) for direct `--gui` or `FORWARD_ARGS`; synced `memory.md` & 5-tier logs; kept `CHANGELOG.md` & `PID 8736`.
- **Verification:** `--help`/`--startup-status` Exit `0`, `rules:check` 22/22, `gitleaks` 0 leaks.
- **Rollback:** Restore from git.

---
## [CHG-20261126-006] - 2026-11-26 02:57:15
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-006_02-57-15.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-006_02-57-15.md)
- **Target Scope:** `git-history-reset-clean-orphan-baseline`
- **Summary:** Orphan git reset on `master` (`clean_root`), purged `ORIG_HEAD`/reflogs/objects (`git gc --prune=now --aggressive`), synced `memory.md` & 5-tier logs, preserved PID `8736`, zero remote push.
- **Verification:** `rev-list --count HEAD == 1`, `show-ref` master-only, `rules:check` 22/22, `gitleaks` 0 leaks.
- **Rollback:** N/A (orphan reset).

---

## [CHG-20261126-005] - 2026-11-26 02:45:20
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-005_2026-11-26_02-45-20.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-005_2026-11-26_02-45-20.md)
- **Target Scope:** `pre-github-cleanup-hygiene-and-governance-sync`
- **Summary:** Pre-GitHub cleanup (`TASK-PRE-GITHUB-CLEANUP-001`): `git rm` `tests/` (36), `temp_prompt/` (110), `archive/` (3), `ui_mockup_prompt.md`, `smart_shutdown_settings.json.bak`; deleted `.pytest_cache/`, 7 `__pycache__/`, `logs/auto_shutdown.log`; updated `.gitignore` (`BOM=False`); compacted `memory.md` (`< 20 KB`), archived older master entries, synced global `memory.md`, preserved live daemon `PID 8736`.
- **Verification:** `npm run rules:check` **22/22 PASS**, `python -B smart_shutdown.py --help` & `py_compile`/import smoke **PASS**, **0** `gitleaks` leaks.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261126-004] - 2026-11-26 02:23:47
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-004_2026-11-26_02-23-47.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-004_2026-11-26_02-23-47.md)
- **Target Scope:** `live-15m-sim-5m-60s-timers-phases-1-to-3`
- **Summary:** Enforce Live Mode `15m` (`900s`) / `60s` inactivity and Simulation Mode `5m` (`300s`) / `60s` inactivity defaults across Smart Shutdown (`TASK-LIVE-15M-SIM-5M-60S-001`): set `DEFAULT_SIMULATION_SECONDS = 300` (`core/models.py`), enforced Live `15m`/`60s` defaults (`core/config.py`), scoped `10.0s` inactivity strictly to `DEMO_30S`/`DEMO_10S` and consumed `DEFAULT_SIMULATION_SECONDS` (`core/coordinator.py`), updated GUI fallbacks & copy (`gui/app_event_bridge.py`, `gui/components/{settings_view,settings_deck,mini_overlay}.py`, `gui/settings_window.py`), healed `smart_shutdown_settings.json` + `.bak` (`15`/`60`/`300`) and reconciled `Smart_Shutdown.lnk` (`--mini-hud --countdown 900 --idle-buffer 60`), and aligned 11 regression test suites (`test_combined_gui_health_audit.py`, `test_config.py`, `test_coordinator.py`, `test_core_gui_sync_contracts.py`, `test_demo_mode_lifecycle_parity.py`, `test_input_hook_coordinator.py`, `test_integration.py`, `test_mini_hud_cancel_behavior.py`, `test_mode_switching_parity.py`, `test_settings_view.py`, `test_unified_gui.py`). Updated `CHANGELOG.md`, synced workspace & global `memory.md`, and pruned `temp_prompt/live_15m_sim_5m_60s_timers/`.
- **Verification:** Independent QA Grade A+ PASS (`AUTH-MGR-20261126-TIMING-QA-001`): **346/346** tests PASSED (`python -m unittest discover -s tests -v`, `44.509s`, Exit Code 0), **21/21** Rule 28 & UTF-8 BOM PASS, **22/22** `npm run rules:check`, **0** `gitleaks` leaks (`201` commits).
- **Rollback:** Restore from git or backup.

---

## [CHG-20261126-003] - 2026-11-26 01:55:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-003_2026-11-26_01-55-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-003_2026-11-26_01-55-00.md)
- **Target Scope:** `status-3state-running-sync-phases-1-to-3`
- **Summary:** Restore `RUNNING` (`[ ⏱️ Running ]` / `⏱️ Running` / `Countdown Running`) for shutdown countdown (`COUNTDOWN_ACTIVE`) and synchronize 3-state physical presence (`Idle`, `Active`, `Away`) across Smart Shutdown (`TASK-STATUS-3STATE-AND-RUNNING-SYNC-001`): added `_PILL_RUNNING` and 3-state `resolve_sentinel_pill_state`/`resolve_presence_phase` (`gui/components/status_resolver.py`), restored `SentinelState.RUNNING` and split `_SENTINEL_RULES` (`gui/components/title_bar.py`), updated `_toggle_pause` fallback and `_update_sentinel_badge` (`gui/components/mini_overlay.py`), updated countdown banner copy (`gui/components/status_formatter.py`), preserved `DISARMED` across `("IDLE", "ACTIVE", "AWAY")` (`gui/app_event_bridge.py`), and aligned 10 regression test suites (`test_compact_ui_redesign.py`, `test_core_gui_sync_contracts.py`, `test_dashboard_view.py`, `test_dual_timers.py`, `test_dynamic_status_pills.py`, `test_mini_hud_controls.py`, `test_status_display_sync.py`, `test_telemetry_sparklines.py`, `test_title_bar_cluster.py`, `test_unified_gui.py`). Updated `CHANGELOG.md`, synced workspace & global `memory.md`, and pruned `temp_prompt/status_3state_running_sync/`.
- **Verification:** Independent QA Grade A+ PASS (`AUTH-MGR-20261126-3STATE-RUN-QA-001`): **346/346** tests PASSED (`python -m unittest discover -s tests -v`, `42.871s`, Exit Code 0), **15/15** Rule 28 & UTF-8 BOM PASS, **22/22** `npm run rules:check`, **0** `gitleaks` leaks.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261126-002] - 2026-11-26 01:40:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-002_2026-11-26_01-40-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-002_2026-11-26_01-40-00.md)
- **Target Scope:** `simulation-mode-1min-default-phases-1-to-3`
- **Summary:** Set default Simulation Mode timer to 1 minute (`60s`) with fast-test `10s` Demo inactivity/grace timings (`TASK-SIMULATION-1MIN-DEFAULT-001`): added `DEFAULT_SIMULATION_SECONDS = 60` and `resolve_mode_duration_seconds()` (`core/models.py`), `SettingsConfig.simulation_timer_sec` clamped `10..3600` (`core/config.py`), scoped `--countdown` CLI override (`smart_shutdown.py`), `Simulation Duration (seconds)` slider and `'1m simulation'` subtitle (`gui/components/settings_view.py`), `simulation_timer_sec` forwarding (`gui/components/settings_deck.py`, `gui/settings_window.py`), and aligned 10 test suites (`test_combined_gui_health_audit.py`, `test_coordinator.py`, `test_core_gui_sync_contracts.py`, `test_demo_mode_lifecycle_parity.py`, `test_input_hook_coordinator.py`, `test_integration.py`, `test_mini_hud_cancel_behavior.py`, `test_mode_switching_parity.py`, `test_settings_view.py`, `test_unified_gui.py`). Updated `CHANGELOG.md`, synced workspace & global `memory.md`, and pruned `temp_prompt/simulation_mode_1min_default/`.
- **Verification:** Independent QA Grade A+ PASS (`AUTH-MGR-20261126-SIM60-QA-001`): **346/346** tests PASSED (`python -m unittest discover -s tests -v`, `44.506s`, Exit Code 0), **19/19** Rule 28 & UTF-8 BOM PASS, **22/22** `npm run rules:check`, **0** `gitleaks` leaks.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261126-001] - 2026-11-26 01:24:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261126-001_2026-11-26_01-24-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-26/change_CHG-20261126-001_2026-11-26_01-24-00.md)
- **Target Scope:** `status-idle-default-fix-qa-and-governance`
- **Summary:** Default startup and no-timer status to `Idle` with 3-state `Idle` / `Active` / `Away` synchronization (`TASK-STATUS-IDLE-DEFAULT-FIX-001`): emitted `has_user_input` in `core/coordinator.py`, updated `gui/components/status_resolver.py`, `gui/app_event_bridge.py`, `gui/unified_app.py`, `gui/components/{title_bar,mini_overlay,circular_gauge,dashboard_view,telemetry_view}.py`, and aligned 5 regression test suites (`test_status_display_sync.py`, `test_dynamic_status_pills.py`, `test_dual_timers.py`, `test_telemetry_sparklines.py`, `test_title_bar_cluster.py`). Synced workspace & global `memory.md` and pruned `temp_prompt/status_idle_default_fix/`.
- **Verification:** Independent QA Grade A+ PASS (`AUTH-MGR-20261126-SIDF-QA-001`): **346/346** tests PASSED (`python -m unittest discover -s tests -v`, `40.468s`, Exit Code 0), **14/14** Rule 28 & UTF-8 BOM PASS, **22/22** `npm run rules:check`, **0** `gitleaks` leaks.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261125-005] - 2026-11-25 23:05:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261125-005_2026-11-25_23-05-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-25/change_CHG-20261125-005_2026-11-25_23-05-00.md)
- **Target Scope:** `status-display-sync-fix-phases-1-to-4`
- **Summary:** Unify Active/Away Status Display (`TASK-STATUS-DISPLAY-SYNC-FIX-001`): simplified state model to `Active (0s..threshold) -> Away (Countdown Active)` removing the 5s `Idle` state (Q1), unified status labels across `CircularCountdownGauge`, `TelemetryView`, `TitleBarComponent`, `FloatingMiniOverlay`, and `UnifiedSentinelApp.pill_status` (Q2), and resolved all 5 root-cause bugs — Bug A (startup `idle_sec=None` `Idle` flash), Bug B (Mini HUD `_toggle_pause` hardcoded `"Away"`), Bug C (`SentinelCoordinator.resume_countdown`/`snooze_countdown` stale `baseline_input_tick`), Bug D (`COUNTDOWN_ACTIVE` `< 5s` `Active` flicker), and Bug E (stale `idle_sec` on Cancel/Mode Switch & raw `state_name` on `pill_status`). Added `tests/test_status_display_sync.py`, synced workspace & global `memory.md` + `CHANGELOG.md`, and pruned `temp_prompt/status_display_sync_fix/`.
- **Verification:** Independent QA Grade A+ PASS: **338/338** tests PASSED (`python -m unittest discover -s tests -v`, `40.523s`, Exit Code 0), **22/22** `npm run rules:check`, **0** `gitleaks` leaks.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261125-004] - 2026-11-25 22:50:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261125-004_2026-11-25_22-50-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-25/change_CHG-20261125-004_2026-11-25_22-50-00.md)
- **Target Scope:** `mini-hud-shutdown-persistence-phases-1-to-4`
- **Commits:** `e8cfbc9` + Phase 4 closure commit
- **Summary:** Complete Mini HUD Default Startup & Shutdown-Resilient Persistence Fix (`TASK-MINI-HUD-SHUTDOWN-PERSISTENCE-001`): extracted atomic `core/settings_store.py` (`temp` + `flush` + `os.fsync` + `.json.bak` rotation + `os.replace` & recovery), flipped `SettingsConfig.mini_hud_on_startup` default to `True`, guarded stale PID `taskkill`, added `--no-mini-hud`/`--full-gui` CLI opt-out in `smart_shutdown.py`, flushed logs & released lock before live shutdown in `core/coordinator.py`, added `reconcile_startup_shortcut` & tokenized `--mini-hud` matching in `core/startup.py`, aligned `settings_view.py`, `settings_app_grid.py`, `settings_deck.py`, `settings_window.py`, and `app_event_bridge.py`, healed live `smart_shutdown_settings.json` + `.json.bak` + `Smart_Shutdown.lnk`, added `tests/test_mini_hud_shutdown_persistence.py`, synced workspace & global `memory.md` + `CHANGELOG.md`, and pruned `temp_prompt/mini_hud_shutdown_persistence_fix/`.
- **Verification:** Independent QA Grade A+ PASS: **337/337** tests PASSED (`python -m unittest discover -s tests -v`, `49.680s`, Exit Code 0), **22/22** `npm run rules:check`, **0** `gitleaks` leaks, live `Smart_Shutdown.lnk` & `smart_shutdown_settings.json` COM/JSON verified.
- **Rollback:** Restore from git or `.json.bak` / backup.

---

## [CHG-20261125-003] - 2026-11-25 04:08:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261125-003_2026-11-25_04-08-00.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/entries/2026-11-25/change_CHG-20261125-003_2026-11-25_04-08-00.md)
- **Target Scope:** `post-rename-verification-phases-1-to-4`
- **Commits:** `e3e7de0`, `d8af850`
- **Summary:** Complete Post-Rename Verification & Core/GUI Sync Audit (`TASK-POST-RENAME-VERIFICATION-001`) following the outer folder rename to `Desktop\Smart Shutdown`: regenerated `Smart_Shutdown.lnk`, prepended UTF-8 BOM to `tests/conftest.py` (`e3e7de0`), fixed 11 `core/` & `gui/` sync defects (dual-timer retention, Demo scaling, snooze/grace pills, slider labels, WASAPI audio & network threshold alignment, bidirectional tray `toggle_mini_hud`, `startup_matches_settings`) + added `tests/test_core_gui_sync_contracts.py` (`d8af850`), synced workspace & global `memory.md` + `CHANGELOG.md`, and pruned `temp_prompt/post_rename_verification/`.
- **Verification:** Independent QA Grade A+ PASS: **311/311** tests PASSED (`python -m unittest discover -s tests -v`, `30.706s`, Exit Code 0), **22/22** `npm run rules:check`, **0** `gitleaks` leaks, `Smart_Shutdown.lnk` COM verified on `Desktop\Smart Shutdown`.
- **Rollback:** Restore from git or backup.

---

## [CHG-20261125-002] - 2026-11-25 03:25:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261125-001_smart_shutdown_rename.md`](file:///c:/Users/Atul%20Verma/Desktop/AntiGravity%20Auto%20Shutdown/changes_log/entries/2026-11-25/change_CHG-20261125-001_smart_shutdown_rename.md)
- **Target Scope:** `smart-shutdown-rename-phases-1-to-6a`
- **Summary:** Execute Smart Shutdown Full Product & Application Rename (`TASK-SMART-SHUTDOWN-RENAME-001`): rename package/CLI/launcher/startup/tray/GUI branding to Smart Shutdown (`smart-shutdown`, `smart_shutdown.py`, `Smart_Shutdown.bat`, `Smart_Shutdown.lnk`), split `core/gui_widgets.py` (`131` lines) & compact `core/gui.py` (`347` lines), preserve external Antigravity IDE/AI monitoring targets, align tests, compact `memory.md` `< 24 KB`, update `CHANGELOG.md` & 5-tier logs, and verify outer folder CWD lock.
- **Verification:** Step 6A governance complete (`READY_FOR_QA_CERTIFICATION`); pending Step 6B Independent QA Certification (`unittest`, `smart_shutdown.py --help`, `npm run rules:check`, `gitleaks`).
- **Rollback:** Restore from git or backup.

---

## [CHG-20261125-001] - 2026-11-25 03:20:00
- **Author:** Atul Verma (`aiprincekumar` / `aiprincekumar010100@gmail.com`)
- **Entry File:** [`change_CHG-20261125-001_2026-11-25_03-20-00.md`](file:///c:/Users/Atul%20Verma/Desktop/AntiGravity%20Auto%20Shutdown/changes_log/entries/2026-11-25/change_CHG-20261125-001_2026-11-25_03-20-00.md)
- **Target Scope:** `combined-gui-health-audit-phases-1-to-5`
- **Commits:** `a47b9a5`, `2c40068`, `c6532c7`, `4b7a9c4`, `03899fd`, `412f0c8`
- **Summary:** Complete Combined GUI & Core Health Audit (`TASK-COMBINED-GUI-HEALTH-AUDIT-001`) across Phases 1–5: backend decoupling & multi-action power (`a47b9a5`), live telemetry collector & tray safety (`2c40068`), GUI component fixes & PEP 562 lazy barrels (`c6532c7`), `app_event_bridge.py` extraction & `unified_app.py` compaction (`4b7a9c4`), and Phase 5 QA suites & assertion alignment (`03899fd`, `412f0c8`).
- **Verification:** 302/302 tests PASSED (`python -m unittest discover -s tests -v`, 32.219s, Exit Code 0), 37/37 Rule 28 & UTF-8 BOM, 22/22 `npm run rules:check`, 0 `gitleaks` leaks
- **Rollback:** Restore from git or backup.

---

## [CHG-20261124-006 .. CHG-20261101-001] - Archived
> Historical entries (`2026-11-01` to `2026-11-24`) are archived in [`master_changes_log_archive_2026-11.md`](file:///c:/Users/Atul%20Verma/Desktop/Smart%20Shutdown/changes_log/master/master_changes_log_archive_2026-11.md).
