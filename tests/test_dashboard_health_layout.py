# -*- coding: utf-8 -*-
"""
tests.test_dashboard_health_layout: Battery 5 offscreen Tkinter layout geometry suite.
Verifies 780x520, 780x520 -> 720x500 resize, fresh 720x500, worst-case busy telemetry,
compact fallback, Compact/Studio view switching, 268x268 gauge, and 36px action pills.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from contextlib import ExitStack
import tkinter as tk
import tkinter.font as tkfont
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.config import SettingsConfig
from gui.unified_app import UnifiedSentinelApp

_WORST_CASE_TELEMETRY = {
    "state": "AI_EVALUATION",
    "target_mode": "SIMULATION",
    "cpu_percent": 24.5,
    "net_total_kb": 64.2,
    "subagent_count": 1,
    "workers": 1,
    "ai_state": "WORKING",
    "audio_inhibit_enabled": True,
    "audio_active": True,
    "is_tree_busy": True,
    "worker_count": 4,
    "memory_mb": 1024,
    "idle_sec": 45,
    "inactivity_threshold_sec": 60,
}


def _enter_layout_patches(stack: ExitStack) -> None:
    """Apply strict hermetic isolation patches before constructing UnifiedSentinelApp."""
    net_obj = SimpleNamespace(bytes_recv=0, bytes_sent=0)
    for cm in (
        patch("gui.unified_app.create_system_tray_icon", side_effect=lambda *a, **k: None),
        patch("gui.app_event_bridge.save_settings_config", return_value=True),
        patch("gui.app_event_bridge.sync_windows_startup", return_value=None),
        patch("gui.components.settings_view.is_startup_enabled", return_value=False),
        patch("core.audio.is_audio_stream_active", return_value=False),
        patch(
            "core.process_tree.get_process_tree_telemetry",
            return_value={"active_pids": [], "worker_count": 0, "memory_mb": 0, "is_tree_busy": False},
        ),
        patch("core.process_tree.is_process_tree_busy", return_value=False),
        patch("psutil.cpu_percent", return_value=2.0),
        patch("psutil.net_io_counters", return_value=net_obj),
        patch("core.input_hook.get_last_input_tick", return_value=1000),
        patch("core.input_hook.get_user_idle_seconds", return_value=0.0),
        patch("core.input_hook.get_idle_seconds", return_value=0.0),
    ):
        stack.enter_context(cm)


def _create_offscreen_app(width: int, height: int) -> UnifiedSentinelApp:
    """Instantiate UnifiedSentinelApp offscreen with alpha=0.0 and settle geometry."""
    cfg = SettingsConfig(audio_inhibit_enabled=True, execution_mode="Simulation")
    app = UnifiedSentinelApp(config=cfg, dry_run=True, auto_start=False)
    app.attributes("-alpha", 0.0)
    app.geometry(f"{width}x{height}+-2500+-2500")
    app.update_idletasks()
    app.update()
    return app


def _assert_studio_geometry(case: unittest.TestCase, app: UnifiedSentinelApp) -> None:
    """Assert right_col, floating health cards, eligibility banner, gauge, and pills fit bounds."""
    dv = app.dashboard_view
    rc_w, rc_h = dv.right_col.winfo_width(), dv.right_col.winfo_height()
    case.assertGreater(rc_w, 0)
    case.assertGreater(rc_h, 0)
    case.assertLessEqual(dv.right_col.winfo_reqheight(), rc_h)
    case.assertLessEqual(dv.eligibility_card.winfo_y() + dv.eligibility_card.winfo_height(), rc_h)
    case.assertLessEqual(dv.eligibility_card.winfo_reqheight(), dv.eligibility_card.winfo_height())

    cards = [w for w in dv.health_card.winfo_children() if isinstance(w, tk.Frame)]
    case.assertEqual(len(cards), 6)
    hc_h = dv.health_card.winfo_height()
    for card in cards:
        case.assertLessEqual(card.winfo_reqwidth(), rc_w)
        case.assertLessEqual(card.winfo_reqwidth(), 335)
        case.assertLessEqual(card.winfo_y() + card.winfo_height(), hc_h)

    case.assertEqual(dv.gauge_card.canvas.winfo_width(), 268)
    case.assertEqual(dv.gauge_card.canvas.winfo_height(), 268)
    case.assertLessEqual(dv.left_col.winfo_reqheight(), dv.left_col.winfo_height())
    for btn in (dv.btn_pause, dv.btn_snooze, dv.btn_monitor, dv.btn_abort, dv.btn_bypass, dv.btn_shutdown):
        case.assertEqual(btn.winfo_height(), btn._curr_h)
        case.assertEqual(btn.winfo_reqheight(), btn.winfo_height())
        case.assertIn(btn.winfo_height(), (36, 38))
        tw = tkfont.Font(font=btn.cget("font")).measure(btn.cget("text"))
        bw = btn.winfo_width()
        case.assertLess(tw, bw, f"Pill '{btn.cget('text')}' text {tw}px >= width {bw}px")


def _apply_busy_and_compact_checks(case: unittest.TestCase, app: UnifiedSentinelApp) -> None:
    """Populate worst-case busy and 12W compact telemetry and assert geometry after each."""
    dv = app.dashboard_view
    app._handle_telemetry_data_event(_WORST_CASE_TELEMETRY)
    app.update_idletasks()
    app.update()
    case.assertEqual(dv.chip_tree.cget("text"), "Busy (4 workers / 1024 MB)")
    case.assertEqual(dv.chip_audio.cget("text"), "[ 🔊 Playing ]")
    case.assertEqual(dv.chip_ai.cget("text"), "Active AI Work (1 Active)")
    _assert_studio_geometry(case, app)

    app._handle_telemetry_data_event({"is_tree_busy": True, "worker_count": 12, "memory_mb": 2048})
    app.update_idletasks()
    app.update()
    case.assertEqual(dv.chip_tree.cget("text"), "Busy (12W / 2048 MB)")
    _assert_studio_geometry(case, app)


class TestDashboardHealthLayout(unittest.TestCase):
    """Battery 5: Offscreen Tk layout geometry validation across 780x520 and 720x500."""

    def test_default_780x520_and_resize_to_720x500(self) -> None:
        with ExitStack() as stack:
            _enter_layout_patches(stack)
            app = _create_offscreen_app(780, 520)
            try:
                _apply_busy_and_compact_checks(self, app)
                app.geometry("720x500+-2500+-2500")
                app.update_idletasks()
                app.update()
                _apply_busy_and_compact_checks(self, app)
            finally:
                app.destroy()

    def test_fresh_720x500_busy_and_compact_fallback(self) -> None:
        with ExitStack() as stack:
            _enter_layout_patches(stack)
            app = _create_offscreen_app(720, 500)
            try:
                _apply_busy_and_compact_checks(self, app)
            finally:
                app.destroy()

    def test_compact_and_studio_view_toggling(self) -> None:
        with ExitStack() as stack:
            _enter_layout_patches(stack)
            app = _create_offscreen_app(720, 500)
            try:
                dv = app.dashboard_view
                app._handle_telemetry_data_event(_WORST_CASE_TELEMETRY)
                dv.set_compact_view()
                app.update_idletasks()
                app.update()
                self.assertFalse(dv.is_studio_view)
                self.assertEqual(dv.left_col.winfo_manager(), "pack")
                self.assertEqual(dv.right_col.winfo_manager(), "pack")
                cards = [w for w in dv.health_card.winfo_children() if isinstance(w, tk.Frame)]
                self.assertEqual(len(cards), 6)
                for card in cards:
                    self.assertLessEqual(card.winfo_reqwidth(), 335)
                    self.assertGreater(card.winfo_height(), 0)
                self.assertGreater(dv.eligibility_card.winfo_height(), 0)

                dv.set_studio_view(True)
                app.update_idletasks()
                app.update()
                self.assertTrue(dv.is_studio_view)
                self.assertEqual(dv.left_col.winfo_manager(), "grid")
                self.assertEqual(dv.right_col.winfo_manager(), "grid")
                _assert_studio_geometry(self, app)
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
