## [unreleased]

### 🚀 Features

- *(timers)* Enforce Live Mode `15m` (`900s`) / `60s` inactivity and Simulation Mode `5m` (`300s`) / `60s` inactivity defaults across `core/models.py`, `core/config.py`, `core/coordinator.py`, GUI bridges/settings/Mini HUD, persisted `smart_shutdown_settings.json` + `.bak`, `Smart_Shutdown.lnk`, and 11 regression test suites (`TASK-LIVE-15M-SIM-5M-60S-001`)
- *(simulation)* Configure 1-minute (60s) default Simulation Mode timer, --countdown override, fast-test Demo timings (10s inactivity/grace), and Settings duration slider
- *(branding)* Rename product and application identity from AntiGravity Auto Shutdown to **Smart Shutdown** (`smart-shutdown`, `smart_shutdown.py`, `Smart_Shutdown.bat`, `Smart_Shutdown.lnk`, `"SmartShutdown"` logger/tray, and `"🛡️ Smart Shutdown"` GUI/HUD titles) while preserving all external Antigravity IDE/AI monitoring targets
- *(audio-detector)* Add separate audio vs video playback detection module
- *(video-idle-detector)* Simplify report card and implement strict in-place terminal overwriting
- *(audio-detector)* Streamline live single-line tracking with track, player, and refresh progress bar
- *(video-detector)* Implement Method 1 SMTC API for WMP and lock 60s idle timer
- *(idle-detector)* Implement 8-field in-place dashboard with 60s idle timer and zero-scrolling ANSI display
- *(game_idle_detector)* Add Windows native GameConfigStore & Xbox Game Bar idle detector
- *(game_idle_detector)* Implement strict 8-field card with in-place zero-scroll rendering
- *(video-detector)* Add audio peak meter, continuous play/pause timers, and 60m activity timeline bar
- *(game-detector)* Add continuous play, pause, audio peak meter, and 60m activity graph
- *(dashboard)* Add continuous play/pause duration, audio peak meter, and 60m activity graph
- *(sentinel)* Migrate keyboard-mouse detector and create dedicated anti-gravity detector with standardized in-place dashboard
- *(input-source)* Add individual keyboard vs mouse activity detection and dynamic dashboard badges
- *(telemetry)* Implement phase 01 core telemetry and sensor metadata enrichment
- *(analytics)* Implement phase 02 reporting and analytics persistence engine
- *(detector)* Align session aggregation with core analyzer blocking architecture to eliminate timer resets
- *(detector)* Add real-time active and inactive chat session counters to dashboard card
- *(hud)* Implement phase 03 native transparent desktop hud overlay
- *(ui)* Remove empty brackets, differentiate root user chats vs subagents, and add window-minutes option
- *(docking)* Implement phase 04 hud docking snapping and tray controller
- *(web)* Implement phase 05 lightweight localhost web dashboard and remote control
- *(release)* Implement phase 06 comprehensive qa verification and master release
- *(structure)* Standardize detector subfolders to clean unified naming matching Anti-Gravity Detector
- *(video-detector)* Add modern video_detector CLI entry point and batch runner
- *(video-detector-hev)* Add video_detector_hev entry point and launcher
- *(hud)* Set default 80% opacity, remove system metrics, integrate timer selectors, and purge 5m auto-shutdown
- *(backend)* Implement Phases 1 to 4 telemetry engine for HUD redesign v3.0
- *(hud)* Implement 3-mode vector canvas and gesture window controller (Phases 5-6)
- *(hud)* Implement default Lock Mode with 1-click toggle icon and menu controls
- *(browser)* Restore Browser Detection subfolder
- *(browser-detection)* Implement RFC 6455 browser WebSocket bridge and connect to Video Detector HUD
- *(browser-detection)* Dynamic YouTube & web media sentinel with single dynamic status button, full title, live progress bar and interactive controls
- *(browser-detection)* Implement dual multi-tabs layout, dynamic auto-switching and interactive volume scrubber
- *(audio)* Synchronize app volume with browser detection in-page volume level
- *(browser-detection)* Implement full-page analytics dashboard and replace popup export/clear buttons with dashboard button
- *(media-controls)* Resolve live vs duration detection, add quality switcher, dual speed controls and advanced window modes
- *(browser-detection)* Implement main-world execution bridge for YouTube volume slider, quality and speed controls
- *(offline)* Integrate Phase 1 - Films & TV (video.ui.exe) real-time metadata, timeline, and playback detection
- *(backend)* Implement JUMP_TO_MEDIA_TAB IPC handler and language preference sync
- *(popup)* Add Switch Tab button and centralized i18n English/Hindi synchronization
- *(dashboard)* Add 1-click language switcher, Switch to Tab hero button, and pure English default system
- *(offline-players)* Implement Phase 2 MPC-HC, MPC-BE, and legacy WMP detection and telemetry
- *(offline-players)* Implement Phase 3 Modern Media Player and multi-tier E2E diagnostic harness
- *(data-hub)* Implement Phase 1 Standalone Multi-Browser SQLite Data Hub daemon with WAL persistence and RFC 6455 WebSocket service
- *(extension)* Implement Phase 2 multi-browser detection, delta sync, offline queue and data hub IPC
- *(dashboard)* Implement Phase 3 multi-browser dropdown filter, Data Hub queries and unified analytics
- *(hud)* Implement Phase 4 HUD decoupling, QUERY_LIVE_STATE subscription and E2E integration test suite
- *(players)* Modularize offline media players into dedicated packages with standalone CLI launchers
- *(players)* Expand universal video player fleet with window mode detection and dedicated launchers
- *(audio)* Implement pure in-app internal volume synchronization via UI Automation and WASAPI session
- *(governance)* Establish project memory, canonical rules mirror, and rules health sentinel

### 🐛 Bug Fixes

- *(status)* Restore `RUNNING` (`[ ⏱️ Running ]` / `⏱️ Running` / `Countdown Running`) for `COUNTDOWN_ACTIVE` and synchronize 3-state physical presence (`Idle`, `Active`, `Away`) across `status_resolver`, `title_bar`, `mini_overlay`, `status_formatter`, `app_event_bridge`, and 10 regression test suites (`TASK-STATUS-3STATE-AND-RUNNING-SYNC-001`)
- *(status)* Unify `Active`/`Away` status display across `SentinelCoordinator`, `status_resolver`, and all GUI surfaces (`CircularCountdownGauge`, `TelemetryView`, `TitleBarComponent`, `FloatingMiniOverlay`, `UnifiedSentinelApp.pill_status`), removing the 5s `Idle` state and fixing startup `idle_sec=None` flash, Mini HUD `_toggle_pause` hardcoded `"Away"`, stale `baseline_input_tick` on resume/snooze, `COUNTDOWN_ACTIVE` `< 5s` flicker, and stale `idle_sec`/raw `state_name` (`TASK-STATUS-DISPLAY-SYNC-FIX-001`)
- *(startup)* Restore Mini HUD default startup, atomic shutdown-resilient settings persistence with `.json.bak` recovery, pre-shutdown log/lock hygiene, and Startup shortcut reconciliation (`TASK-MINI-HUD-SHUTDOWN-PERSISTENCE-001`)
- *(sync)* Align core backend WASAPI audio/network inhibitors, dual-timer retention, Demo settings, snooze/grace pills, slider labels, and bidirectional tray Show/Hide Mini HUD toggle (`d8af850`)
- *(video-idle-detector)* Eliminate win32 desktop deadlock and decoupled powercfg poller
- *(audio-detector)* Resolve cmd.exe multibyte seek corruption in batch runner and add robust python discovery
- *(video-detector)* Implement EVR child window video surface detection for Legacy WMP
- *(wmp-legacy)* Eliminate audio/video/idle flickering for Windows Media Player Legacy
- *(wmp-legacy)* Ignore background library scan and bind playback to active cmdline and window title
- *(wmp-legacy)* Filter out Windows system Default IME window and restore real media title
- *(game-idle-detector)* Quote engine paths in launcher and add sys.path injection to prevent auto-close crash
- *(audio-detector)* Eliminate console window flash, remove os.system subshell, add CREATE_NO_WINDOW and render immediate dashboard frame
- *(launcher)* Eliminate terminal flicker and code flash in Run_Video_Idle_Detector.bat
- *(game_idle_detector)* Eliminate batch launcher flashing and naked ANSI codes with atomic first-frame painting
- *(launcher)* Eliminate prompt flicker and blinking code delay in Run_Audio_Detector.bat
- *(ui)* Remove ANSI 2J full-screen wipe to eliminate initial terminal flash
- *(game-detector)* Eliminate batch launcher blinking code and render 0ms initial frame
- *(launcher)* Mirror Run_Game_Detector.bat structure and restore clean startup
- *(launcher)* Align Run_Video_Idle_Detector.bat and 0ms initial frame with game sentinel pattern
- *(detector)* Resolve anti-gravity state flapping with generic tool tracking, multi-session aggregation, and 5s debounce
- *(tests)* Restore test suites for Video Detector and Video Detector HEV
- *(hud)* Resolve timer selector click handling, state persistence and real-time detector threshold synchronization
- *(hud)* Suppress CMD window with zero-flicker launch and enforce 60s default timer
- *(detection)* Restore SMTC and WASAPI multi-app video and audio detection pipeline
- *(audio-engine)* Resolve master/app volume detection, mute vs pause separation, and playback speed (Phases 1, 4, 5)
- *(hud-ergonomics)* Enforce bottom-right taskbar docking and click debounce disambiguation (Phases 2-3)
- *(telemetry)* Complete real-time pipeline audit and live verification (Phase 6)
- *(media-sentinel)* Resolve live detection freeze, YouTube resolution detection and missing progress bar
- *(offline-player)* Linearize volume curve, restore offline timeline seek tracking, and fix play/pause/mute detection
- *(security)* Eliminate inline onerror event handlers for MV3 CSP compliance in popup and dashboard
- *(timeline)* Restore offline player seek position, duration tracking, and delta-based pause/mute discrimination
- *(vlc)* Restore VLC resolution, duration, playback speed, and dual pause+silence timers
- *(timer)* Enforce exclusive pause timer when video is both paused and muted
- *(media)* Enforce strict 0.25x speed ladder, active refresh animation and videohud protocol auto-launch
- *(media)* Resolve play-pause isolated bridge, stationary refresh icon spin, and zero-prompt native messaging HUD launch
- *(smtc)* Snap mock playback speed to standard speeds ladder and auto-compute seek progress
- *(classifier)* Map video.ui.exe to Films & TV platform tag
- *(scanner)* Recognize Films & TV / Movies & TV generic titles and set platform tag
- *(media-events)* Eliminate multi-channel dispatch duplication and enforce deterministic action cooldown to stop screen flicker
- *(films-tv)* Resolve UWP ApplicationFrameHost process, live SMTC timeline, and HUD real-time display
- *(browser-sentinel)* Resolve JUMP_TO_MEDIA_TAB resolution and relocate toast notifications to bottom for zero layout shift
- *(media-forensics)* Resolve Windows 11 Films & TV, Modern Media Player, and Legacy WMP detection & telemetry
- *(browser-sentinel)* Resolve media tab switch fail-safe discovery and eliminate reload storage reset
- *(data-hub-ui)* Resolve SQLite DB file creation, hub daemon autostart, and single-row compact dashboard header

### 📚 Documentation

- *(governance)* Certify post-rename verification (`TASK-POST-RENAME-VERIFICATION-001`, 311/311 tests PASS), sync workspace/global `memory.md` to `Desktop\Smart Shutdown`, record `CHG-20261125-003` in 5-tier `changes_log/`, and prune `temp_prompt/post_rename_verification/`
- *(memory)* Compact workspace `memory.md` under 24 KB Rule 28 ceiling, sync global `memory.md`, and record `CHG-20261125-002` in 5-tier `changes_log/`
- *(changes_log)* Initialize Universal Rule 6 5-tier changes log and git-cliff changelog
- *(architecture)* Add PRD, TRD, DESIGN, Feature Memory, and Phase Prompts 01-06 for Video Sentinel Enterprise Expansion
- *(hud)* Update complete phase documentation suite for native transparent desktop hud overlay
- *(hud)* Establish immutable architectural memory and rejected features ledger (Rule 15)
- *(hud)* Update master prompt with exhaustive 7-section implementations, 3-mode layouts, and exact pixel maps (Rule 15)
- *(audit)* Create master diagnostic list and phase-wise bugfix prompt (Rule 15)

### ⚡ Performance

- *(hud)* Eliminate command prompt blink and remove 2s startup lag with native GUI launcher and deferred background workers

### 🚜 Refactor

- *(core)* Extract `core/gui_widgets.py` (131 lines) and compact `core/gui.py` (347 lines, < 24 KB, UTF-8 BOM) per Universal Rule 28
- Relocate audio detector module to WindowsIdleDetector/
- Relocate audio detector to windows_idle_detector/windows_audio_detector/
- *(video-sentinel)* Modularize video_idle_detector into high-cohesion single-responsibility subpackages
- *(audio-detector)* Split monolithic script into modular core package architecture
- *(game_idle_detector)* Remove interactive menu and launch live 8-field monitor directly by default
- *(game_idle_detector)* Delete unused option 2-5 functions and code blocks, keeping pure live 8-field sentinel
- *(audio-detector)* Simplify to lean live-monitoring modules, remove diagnostic bloat, and eliminate launcher banner flash
- *(game_idle_detector)* Split into clean modular files (engine, ui, sentinel) and purge all schema 2-4 code
- *(launcher)* Simplify Run_Audio_Detector.bat to pure 2-step direct invocation
- *(architecture)* Decouple monolithic sentinel into clean enterprise modules package
- *(keyboard-mouse)* Decouple monolithic sentinel into clean enterprise modules package
- *(game-detector)* Modularize game detector into enterprise modules package
- *(audio-detector)* Add modules package matching Anti-Gravity Detector standard
- Rename HEV to HUD across project and update links
- *(hud)* Remove timer selector pills from main canvas, preserve right-click menu and compact height to 255px
- *(core)* Migrate hardcoded paths to Path.home() and relocate Browser Detection
- *(structure)* Modularize repository into tests/, docs/, and launchers/

### 🎨 Styling

- *(canvas)* Declutter playing section with vertical row spacing and zero text overlap

### 🧪 Testing

- *(sync)* Add `tests/test_core_gui_sync_contracts.py` regression suite (183 lines) verifying core/GUI inhibitor, dual-timer, Demo, and tray toggle contracts (`d8af850`)
- *(game-detector)* Harden wasapi master audio peak test against real-time hardware audio jitter
- *(qa)* Certify end-to-end regression and smoke suite for HUD redesign v3.0 (Phase 7)
- *(i18n)* Add comprehensive verification suite and enforce pure English dictionary titles

### ⚙️ Miscellaneous Tasks

- *(encoding)* Add UTF-8 BOM (`0xEF,0xBB,0xBF`) to `tests/conftest.py` (`e3e7de0`) and regenerate Windows Startup `Smart_Shutdown.lnk` for `Desktop\Smart Shutdown`
- Create Keyboard and Mouse Detector and Anti-Gravity Detector folders
- Add Keyboard and Mouse Detector and Anti-Gravity Detector folders
- Purge test files and clutter, streamline workspace to essential production files
- *(video-detector-hev)* Preserve reports directory via .gitkeep
- Purge test files and clutter, streamline workspace to essential production files
- *(cleanup)* Purge redundant test files, duplicate core package, and archive backup clutter
- *(cleanup)* Remove phase-wise prompt docs, generated test reports, and pycache
- *(config)* Sync runtime HUD coordinates
- *(cleanup)* Remove unnecessary cache and temporary files
- *(cleanup)* Remove test suite, prompt docs, and redundant launcher artifacts
- *(refactor)* Modularize repository structure, minimize root files, and clean obsolete files
