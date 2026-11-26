# -*- coding: utf-8 -*-
"""
tests.test_dashboard_health_cards: Batteries 1-4 unit & telemetry bridge tests
for DashboardView Audio Stream & Process Tree cards and Rule 28 modularity/BOM invariants.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import ast
from contextlib import ExitStack
from pathlib import Path
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.config import SettingsConfig
from core.coordinator import SentinelCoordinator
from core.models import TargetMode
from core.telemetry_collector import TelemetryCollector, normalize_telemetry_defaults
from gui.app_event_bridge import apply_mode_change, apply_save_settings
from gui.components.dashboard_view import DashboardView
from gui.components.health_summary import (
    format_audio_card,
    format_process_tree_card,
)
from gui.theme import STATUS_AMBER, STATUS_EMERALD, STATUS_SLATE
from gui.unified_app import UnifiedSentinelApp

ROOT_DIR = Path(__file__).resolve().parent.parent
_CONTROL_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)


def _enter_isolation_patches(stack: ExitStack, cpu_pct: float = 2.0, net_rx: int = 0, net_tx: int = 0) -> dict:
    """Apply strict hermetic patches preventing OS, tray, log, or settings mutations."""
    net_obj = SimpleNamespace(bytes_recv=net_rx, bytes_sent=net_tx)
    patches = {
        "tray": patch("gui.unified_app.create_system_tray_icon", side_effect=lambda *a, **k: None),
        "save_cfg": patch("gui.app_event_bridge.save_settings_config", return_value=True),
        "sync_win": patch("gui.app_event_bridge.sync_windows_startup", return_value=None),
        "startup_ro": patch("gui.components.settings_view.is_startup_enabled", return_value=False),
        "audio": patch("core.audio.is_audio_stream_active", return_value=False),
        "tree": patch(
            "core.process_tree.get_process_tree_telemetry",
            return_value={"active_pids": [], "worker_count": 0, "memory_mb": 0, "is_tree_busy": False},
        ),
        "tree_busy": patch("core.process_tree.is_process_tree_busy", return_value=False),
        "cpu": patch("psutil.cpu_percent", return_value=cpu_pct),
        "net": patch("psutil.net_io_counters", return_value=net_obj),
        "tick": patch("core.input_hook.get_last_input_tick", return_value=1000),
        "idle_u": patch("core.input_hook.get_user_idle_seconds", return_value=0.0),
        "idle_g": patch("core.input_hook.get_idle_seconds", return_value=0.0),
    }
    return {name: stack.enter_context(cm) for name, cm in patches.items()}


def _make_offscreen_root() -> tk.Tk:
    """Create a hidden offscreen Tk root window for widget unit tests."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-alpha", 0.0)
    root.geometry("780x520+-2500+-2500")
    return root


def _assert_pill_state(case: unittest.TestCase, canvas: tk.Canvas, active: bool, color: str) -> None:
    """Verify rendered status pill dot coordinates (left=inactive, right=active) and color."""
    items = canvas.find_all()
    case.assertGreaterEqual(len(items), 2)
    coords = canvas.coords(items[-1])
    if active:
        case.assertGreater(coords[0], 20.0)
    else:
        case.assertLess(coords[0], 20.0)
    case.assertEqual(canvas.itemcget(items[-1], "fill"), color)


def _max_ast_depth(node: ast.AST, depth: int = 0) -> int:
    """Compute maximum control-flow nesting depth inside an AST node."""
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        next_depth = depth + 1 if isinstance(child, _CONTROL_NODES) else depth
        best = max(best, _max_ast_depth(child, next_depth))
    return best


class TestCardOrderingAndRule28(unittest.TestCase):
    """Battery 1: Floating health card ordering, widget bindings, Rule 28 & BOM invariants."""

    def test_card_ordering_and_widgets(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            card_frames = [w for w in dv.health_card.winfo_children() if isinstance(w, tk.Frame)]
            self.assertEqual(len(card_frames), 6)
            titles = []
            for frame in card_frames:
                left_box = frame.winfo_children()[0]
                labels = [w for w in left_box.winfo_children() if isinstance(w, tk.Label)]
                titles.append(labels[1].cget("text"))
            self.assertEqual(
                titles,
                ["CPU Activity", "Network Transfer", "Antigravity Task", "Audio Stream", "Process Tree", "User Inactivity"],
            )
            self.assertIsInstance(dv.chip_audio, tk.Label)
            self.assertIsInstance(dv.bar_audio, tk.Canvas)
            self.assertIsInstance(dv.chip_tree, tk.Label)
            self.assertIsInstance(dv.bar_tree, tk.Canvas)
            self.assertEqual(dv.health_cards["audio"], (dv.chip_audio, dv.bar_audio))
            self.assertEqual(dv.health_cards["tree"], (dv.chip_tree, dv.bar_tree))
        finally:
            root.destroy()

    def test_phase1_rule28_bom_and_zero_tkinter(self) -> None:
        budgets = [
            ("gui/components/health_summary.py", 250, 16384),
            ("gui/components/dashboard_view.py", 350, None),
            ("gui/app_event_bridge.py", 350, None),
            ("gui/app_event_handlers.py", 200, None),
            ("gui/unified_app.py", 350, 24576),
            ("core/telemetry_collector.py", 200, None),
            ("core/coordinator_helpers.py", 200, None),
            ("core/coordinator.py", 350, 24576),
        ]
        for rel, max_lines, max_bytes in budgets:
            path = ROOT_DIR / rel
            raw = path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), f"Missing UTF-8 BOM: {rel}")
            lines = raw.decode("utf-8-sig").splitlines()
            self.assertLess(len(lines), max_lines, f"Line budget exceeded: {rel} ({len(lines)})")
            if max_bytes is not None:
                self.assertLess(len(raw), max_bytes, f"Byte budget exceeded: {rel} ({len(raw)})")

        hs_tree = ast.parse((ROOT_DIR / "gui/components/health_summary.py").read_text(encoding="utf-8-sig"))
        for node in ast.walk(hs_tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any("tkinter" in a.name for a in node.names))
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotIn("tkinter", node.module)

    def test_phase2_tests_rule28_ast_and_bom(self) -> None:
        test_files = sorted((ROOT_DIR / "tests").glob("*.py"))
        self.assertGreaterEqual(len(test_files), 3)
        for path in test_files:
            raw = path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), f"Missing UTF-8 BOM: {path.name}")
            self.assertLess(len(raw), 24576, f"Byte budget exceeded: {path.name}")
            src = raw.decode("utf-8-sig")
            self.assertLess(len(src.splitlines()), 400, f"Line budget exceeded: {path.name}")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fn_lines = (node.end_lineno or node.lineno) - node.lineno + 1
                    self.assertLessEqual(fn_lines, 50, f"{path.name}:{node.name} is {fn_lines} lines")
                    self.assertLessEqual(_max_ast_depth(node), 4, f"{path.name}:{node.name} nesting > 4")


class TestAudioStreamCard(unittest.TestCase):
    """Battery 2: Audio Stream 3-state matrix, banner coupling, and partial updates."""

    def test_audio_three_state_matrix_and_banner(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            base = {"state": "IDLE_MONITORING", "idle_sec": 60, "inactivity_threshold_sec": 60}
            cases = [
                ({"audio_inhibit_enabled": True, "audio_active": False}, "[ 🔇 Silent ]", STATUS_EMERALD, False, False),
                ({"audio_inhibit_enabled": True, "audio_active": True}, "[ 🔊 Playing ]", STATUS_AMBER, True, True),
                ({"audio_inhibit_enabled": False, "audio_active": True}, "[ Disabled ]", STATUS_SLATE, False, False),
            ]
            for payload, exp_txt, exp_col, exp_dot, exp_banner in cases:
                with self.subTest(payload=payload):
                    dv.update_health({**base, **payload})
                    self.assertEqual(dv.chip_audio.cget("text"), exp_txt)
                    self.assertEqual(dv.chip_audio.cget("fg"), exp_col)
                    _assert_pill_state(self, dv.bar_audio, exp_dot, exp_col)
                    banner = dv.lbl_eligibility.cget("text")
                    self.assertEqual("Audio Stream Active" in banner, exp_banner)
        finally:
            root.destroy()

    def test_audio_partial_payloads_and_explicit_disable_reset(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            dv.update_health({"audio_inhibit_enabled": True, "audio_active": True})
            dv.update_health({"cpu_percent": 2.5})
            self.assertEqual(dv.chip_audio.cget("text"), "[ 🔊 Playing ]")
            self.assertEqual(dv.chip_audio.cget("fg"), STATUS_AMBER)

            dv.update_health({"audio_inhibit_enabled": False})
            self.assertEqual(dv.chip_audio.cget("text"), "[ Disabled ]")
            self.assertFalse(dv._last_telemetry["audio_active"])
            dv.update_health({"cpu_percent": 3.0})
            self.assertEqual(dv.chip_audio.cget("text"), "[ Disabled ]")
            self.assertEqual(format_audio_card({"audio_inhibit_enabled": False, "audio_active": True}), ("[ Disabled ]", STATUS_SLATE, False))
        finally:
            root.destroy()


class TestProcessTreeCard(unittest.TestCase):
    """Battery 3: Process Tree matrix, compact guard, reset, decoupling, and tooltip."""

    def test_process_tree_state_matrix_and_compact_guard(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            base = {"state": "IDLE_MONITORING", "idle_sec": 60, "inactivity_threshold_sec": 60, "audio_active": False}
            cases = [
                ({"is_tree_busy": False, "worker_count": 0, "memory_mb": 0}, "Idle", STATUS_EMERALD, False, False),
                ({"is_tree_busy": False, "worker_count": 0, "memory_mb": 256}, "Idle (256 MB)", STATUS_EMERALD, False, False),
                ({"is_tree_busy": True, "worker_count": 1, "memory_mb": 256}, "Busy (1 worker / 256 MB)", STATUS_AMBER, True, True),
                ({"is_tree_busy": True, "worker_count": 3, "memory_mb": 512}, "Busy (3 workers / 512 MB)", STATUS_AMBER, True, True),
                ({"is_tree_busy": True, "worker_count": 12, "memory_mb": 2048}, "Busy (12W / 2048 MB)", STATUS_AMBER, True, True),
            ]
            for payload, exp_txt, exp_col, exp_dot, exp_banner in cases:
                with self.subTest(payload=payload):
                    dv.update_health({**base, **payload})
                    self.assertEqual(dv.chip_tree.cget("text"), exp_txt)
                    self.assertLessEqual(len(exp_txt), 26)
                    self.assertEqual(dv.chip_tree.cget("fg"), exp_col)
                    _assert_pill_state(self, dv.bar_tree, exp_dot, exp_col)
                    self.assertEqual("Descendant Processes Busy" in dv.lbl_eligibility.cget("text"), exp_banner)
        finally:
            root.destroy()

    def test_process_tree_zero_worker_fallbacks_and_explicit_reset(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            dv.update_health({"is_tree_busy": True, "idle_sec": 60, "inactivity_threshold_sec": 60})
            self.assertEqual(dv.chip_tree.cget("text"), "Busy [Active]")
            self.assertEqual(dv.chip_tree.cget("fg"), STATUS_AMBER)

            dv.update_health({"is_tree_busy": True, "memory_mb": 512})
            self.assertEqual(dv.chip_tree.cget("text"), "Busy (512 MB)")

            dv.update_health({"is_tree_busy": True, "worker_count": 3, "memory_mb": 0})
            self.assertEqual(dv.chip_tree.cget("text"), "Busy (3 workers / 0 MB)")

            dv.update_health({"is_tree_busy": False})
            self.assertEqual(dv._last_telemetry["worker_count"], 0)
            self.assertEqual(dv.chip_tree.cget("text"), "Idle")
            self.assertEqual(dv.chip_tree.cget("fg"), STATUS_EMERALD)
            self.assertNotIn("Descendant Processes Busy", dv.lbl_eligibility.cget("text"))
        finally:
            root.destroy()

    def test_process_tree_decoupling_partial_and_tooltip(self) -> None:
        root = _make_offscreen_root()
        try:
            dv = DashboardView(root)
            dv.update_health({"subagent_count": 2, "workers": 2, "ai_state": "WORKING"})
            self.assertEqual(dv.chip_ai.cget("text"), "Active AI Work (2 Active)")
            self.assertEqual(dv.chip_tree.cget("text"), "Idle")
            self.assertEqual(format_process_tree_card({"subagent_count": 5, "workers": 5}), ("Idle", STATUS_EMERALD, False))
            self.assertEqual(format_process_tree_card({"active_pids": [11, 22], "memory_mb": 64}), ("Busy (2 workers / 64 MB)", STATUS_AMBER, True))

            dv.update_health({"is_tree_busy": True, "worker_count": 2, "memory_mb": 512, "audio_inhibit_enabled": True, "audio_active": False})
            dv.update_health({"net_total_kb": 1.0})
            self.assertEqual(dv.chip_tree.cget("text"), "Busy (2 workers / 512 MB)")

            tip_silent = dv._format_tooltip_details()
            self.assertIn("Audio: Silent", tip_silent)
            self.assertIn("Tree: Busy 2W (512 MB)", tip_silent)

            dv.update_health({"audio_active": True, "is_tree_busy": False, "memory_mb": 120})
            tip_play = dv._format_tooltip_details()
            self.assertIn("Audio: Playing", tip_play)
            self.assertIn("Tree: 0W (120 MB)", tip_play)

            dv.update_health({"audio_inhibit_enabled": False})
            self.assertIn("Audio: Off", dv._format_tooltip_details())
        finally:
            root.destroy()


def _make_offscreen_app(audio_inhibit_enabled: bool = False) -> UnifiedSentinelApp:
    """Create a withdrawn offscreen UnifiedSentinelApp for bridge/forwarding tests."""
    cfg = SettingsConfig(audio_inhibit_enabled=audio_inhibit_enabled, execution_mode="Simulation")
    app = UnifiedSentinelApp(config=cfg, dry_run=True, auto_start=False)
    app.withdraw()
    app.attributes("-alpha", 0.0)
    app.geometry("780x520+-2500+-2500")
    app.update_idletasks()
    return app


class TestTelemetryBridgeForwarding(unittest.TestCase):
    """Battery 4: Core TelemetryCollector, SentinelCoordinator, Bridge, and UnifiedSentinelApp sync."""

    def test_collector_sample_and_normalize_defaults(self) -> None:
        with ExitStack() as stack:
            mocks = _enter_isolation_patches(stack, cpu_pct=12.4)
            mocks["audio"].return_value = True
            mocks["tree"].return_value = {"active_pids": [41, 42], "worker_count": 2, "memory_mb": 320, "is_tree_busy": True}
            collector = TelemetryCollector()
            snap = collector.sample(SettingsConfig(audio_inhibit_enabled=True))
            self.assertEqual((snap["audio_active"], snap["audio_inhibit_enabled"], snap["worker_count"], snap["is_tree_busy"], snap["memory_mb"]), (True, True, 2, True, 320))

            mocks["audio"].reset_mock()
            snap_off = collector.sample(SettingsConfig(audio_inhibit_enabled=False))
            self.assertFalse(snap_off["audio_active"])
            self.assertFalse(snap_off["audio_inhibit_enabled"])
            mocks["audio"].assert_not_called()

        norm = normalize_telemetry_defaults({"audio_active": True}, SettingsConfig(audio_inhibit_enabled=False))
        self.assertEqual((norm["audio_inhibit_enabled"], norm["audio_active"], norm["worker_count"], norm["is_tree_busy"], norm["memory_mb"]), (False, False, 0, False, 0))

    def test_coordinator_update_config_and_process_tree_blocker(self) -> None:
        with ExitStack() as stack:
            mocks = _enter_isolation_patches(stack)
            coord = SentinelCoordinator(config=SettingsConfig(audio_inhibit_enabled=True), dry_run=True)
            coord._last_hw_telemetry = {"audio_active": True, "worker_count": 2, "memory_mb": 300, "is_tree_busy": True}
            coord.update_config(SettingsConfig(audio_inhibit_enabled=False))

            events = []
            while not coord.event_queue.empty():
                events.append(coord.event_queue.get_nowait())
            telem_evs = [e for e in events if e.event_type == "TELEMETRY"]
            self.assertTrue(telem_evs)
            self.assertFalse(telem_evs[-1].data["audio_inhibit_enabled"])
            self.assertFalse(telem_evs[-1].data["audio_active"])

            mocks["tree_busy"].return_value = True
            res = coord._evaluate_system_blockers({"active_count": 0, "sessions": []})
            self.assertEqual(res["status"], "AI_BUSY_PROCESS")
            ev = coord.event_queue.get_nowait()
            self.assertEqual(ev.event_type, "STATE_CHANGE")
            self.assertEqual(ev.data.get("reason"), "process_tree_busy")
            self.assertTrue(ev.data.get("is_tree_busy"))

    def test_app_startup_telemetry_state_change_and_cancel_forwarding(self) -> None:
        with ExitStack() as stack:
            _enter_isolation_patches(stack)
            app = _make_offscreen_app(audio_inhibit_enabled=False)
            try:
                self.assertEqual(app.dashboard_view.chip_audio.cget("text"), "[ Disabled ]")
                app._handle_telemetry_data_event({
                    "state": "AI_EVALUATION", "audio_inhibit_enabled": True, "audio_active": True,
                    "worker_count": 2, "is_tree_busy": True, "memory_mb": 512,
                })
                self.assertEqual(app.dashboard_view.chip_audio.cget("text"), "[ 🔊 Playing ]")
                self.assertEqual(app.dashboard_view.chip_tree.cget("text"), "Busy (2 workers / 512 MB)")

                app._handle_state_change_event({"state": "IDLE_MONITORING", "reason": "user_active"})
                self.assertFalse(app.dashboard_view._last_telemetry["is_tree_busy"])
                self.assertEqual(app.dashboard_view._last_telemetry["worker_count"], 0)
                self.assertEqual(app.dashboard_view.chip_tree.cget("text"), "Idle (512 MB)")

                app._handle_telemetry_data_event({"is_tree_busy": True, "worker_count": 3, "memory_mb": 256})
                app._on_cancel_clicked()
                self.assertFalse(app.dashboard_view._last_telemetry["is_tree_busy"])
                self.assertEqual(app.dashboard_view._last_telemetry["worker_count"], 0)
                self.assertEqual(app.dashboard_view.chip_tree.cget("text"), "Idle")
            finally:
                app.destroy()

    def test_apply_save_settings_and_mode_change_sync(self) -> None:
        with ExitStack() as stack:
            mocks = _enter_isolation_patches(stack)
            app = _make_offscreen_app(audio_inhibit_enabled=False)
            try:
                app._last_telemetry_snapshot["audio_active"] = True
                app._last_telemetry_snapshot["idle_sec"] = 60
                apply_save_settings(app, SettingsConfig(audio_inhibit_enabled=True, execution_mode="Simulation"))
                self.assertTrue(app._last_telemetry_snapshot["audio_inhibit_enabled"])
                self.assertEqual(app.dashboard_view.chip_audio.cget("text"), "[ 🔊 Playing ]")
                self.assertIn("Audio Stream Active", app.dashboard_view.lbl_eligibility.cget("text"))

                apply_save_settings(app, SettingsConfig(audio_inhibit_enabled=False, execution_mode="Simulation"))
                self.assertEqual(app.dashboard_view.chip_audio.cget("text"), "[ Disabled ]")
                self.assertNotIn("Audio Stream Active", app.dashboard_view.lbl_eligibility.cget("text"))
                mocks["save_cfg"].assert_not_called()
                mocks["sync_win"].assert_not_called()

                app._handle_telemetry_data_event({"is_tree_busy": True, "worker_count": 3, "memory_mb": 512})
                apply_mode_change(app, TargetMode.DEMO_30S)
                self.assertFalse(app.dashboard_view._last_telemetry["is_tree_busy"])
                self.assertEqual(app.dashboard_view._last_telemetry["worker_count"], 0)
                self.assertEqual(app.dashboard_view.chip_tree.cget("text"), "Idle")
                self.assertEqual(app.dashboard_view.chip_audio.cget("text"), "[ Disabled ]")
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
