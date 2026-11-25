# -*- coding: utf-8 -*-
"""
core.system_tray: Windows 11 notification area / system tray integration.
Provides background docking, detached event loop via pystray, and context menu.
Department 05 Frontend and Desktop / Department 06 Backend and Systems Engineering.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import logging
import threading
from typing import Optional, Any

try:
    import tkinter as tk
    _TK_ERRORS = (tk.TclError, RuntimeError)
except Exception:
    tk = None  # type: ignore
    _TK_ERRORS = (RuntimeError,)

logger_instance = logging.getLogger("SmartShutdown")

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    PIL_AVAILABLE = False

try:
    import pystray
    from pystray import MenuItem as item, Menu as menu
    PYSTRAY_AVAILABLE = True
except ImportError:
    pystray = None  # type: ignore
    item = None  # type: ignore
    menu = None  # type: ignore
    PYSTRAY_AVAILABLE = False

try:
    from core.monitor_power import toggle_monitor_power_off
except ImportError:
    def toggle_monitor_power_off() -> bool:
        return False


def _create_default_tray_image(width: int = 64, height: int = 64) -> Optional[Any]:
    """Generates a custom cyan/emerald shield icon for the Windows notification tray."""
    if not PIL_AVAILABLE or Image is None or ImageDraw is None:
        return None
    try:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        pts = [
            (width // 2, 4), (width - 6, 14), (width - 12, height - 16),
            (width // 2, height - 4), (12, height - 16), (6, 14),
        ]
        draw.polygon(pts, fill="#06B6D4", outline="#38BDF8")
        inner = [
            (width // 2, 14), (width - 14, 22), (width - 18, height - 22),
            (width // 2, height - 12), (18, height - 22), (14, 22),
        ]
        draw.polygon(inner, fill="#0F172A", outline="#06B6D4")
        return img
    except Exception as exc:
        logger_instance.warning(f"[SYSTEM_TRAY] Failed to create tray image: {exc}")
        return None


def _safe_dispatch(app: Any, method_name: str, *args) -> None:
    """Dispatch a callback safely onto Tkinter's main event loop if alive."""
    if app is None or not getattr(app, "_is_running", True):
        return

    def _call() -> None:
        if not getattr(app, "_is_running", True):
            return
        fn = getattr(app, method_name, None)
        if not callable(fn):
            return
        try:
            fn(*args)
        except _TK_ERRORS as exc:
            logger_instance.debug(f"[SYSTEM_TRAY] Skipping {method_name} after Tk teardown: {exc}")
        except Exception as exc:
            logger_instance.error(f"[SYSTEM_TRAY] Error invoking {method_name}: {exc}")

    if hasattr(app, "after") and callable(app.after):
        try:
            if hasattr(app, "winfo_exists") and not app.winfo_exists():
                return
            app.after(0, _call)
            return
        except _TK_ERRORS as exc:
            logger_instance.debug(f"[SYSTEM_TRAY] Tk loop unavailable for {method_name}: {exc}")
            return
        except Exception:
            pass
    _call()


def _dispatch_toggle_monitor(app_reference: Any) -> None:
    """Route monitor toggle through app handler when available, else direct DPMS helper."""
    if hasattr(app_reference, "_on_toggle_monitor_clicked"):
        _safe_dispatch(app_reference, "_on_toggle_monitor_clicked")
    else:
        toggle_monitor_power_off()


def _dispatch_toggle_mini_hud(app_reference: Any) -> None:
    """Toggle Mini HUD visibility if supported, else fall back to restore_mini_hud."""
    method = "toggle_mini_hud" if hasattr(app_reference, "toggle_mini_hud") else "restore_mini_hud"
    _safe_dispatch(app_reference, method)


def create_system_tray_icon(app_reference: Any) -> Optional[Any]:
    """
    Constructs a pystray Icon instance bound to the master application.
    Returns None gracefully if pystray or PIL is not installed or headless.
    """
    if not PYSTRAY_AVAILABLE or pystray is None or menu is None or item is None:
        logger_instance.info("[SYSTEM_TRAY] pystray not installed; system tray running in fallback mode.")
        return None

    img = _create_default_tray_image()
    if img is None:
        return None

    tray_menu = menu(
        item("Show Cockpit", lambda _icon, _item: _safe_dispatch(app_reference, "restore_master_window")),
        item("🪟 Show / Hide Mini HUD", lambda _icon, _item: _dispatch_toggle_mini_hud(app_reference)),
        item("⏸️ Pause / Resume", lambda _icon, _item: _safe_dispatch(app_reference, "_on_pause_clicked")),
        item("💤 +15m Snooze", lambda _icon, _item: _safe_dispatch(app_reference, "_on_snooze_clicked", 900)),
        item("🖥️ Toggle Monitor", lambda _icon, _item: _dispatch_toggle_monitor(app_reference)),
        item("✕ Exit Smart Shutdown", lambda _icon, _item: _safe_dispatch(app_reference, "_shutdown_and_exit")),
    )

    try:
        return pystray.Icon(
            name="SmartShutdown",
            icon=img,
            title="Smart Shutdown Cockpit",
            menu=tray_menu,
        )
    except Exception as exc:
        logger_instance.warning(f"[SYSTEM_TRAY] Failed to initialize pystray.Icon: {exc}")
        return None


def start_tray_icon(icon: Optional[Any]) -> bool:
    """Launches the system tray icon using run_detached() or a daemon thread."""
    if icon is None:
        return False
    if hasattr(icon, "run_detached"):
        try:
            icon.run_detached()
            logger_instance.info("[SYSTEM_TRAY] System tray icon running detached.")
            return True
        except Exception as exc:
            logger_instance.warning(f"[SYSTEM_TRAY] run_detached failed: {exc}; launching daemon thread.")
    if hasattr(icon, "run"):
        try:
            t = threading.Thread(target=icon.run, daemon=True, name="SystemTrayWorkerThread")
            t.start()
            return True
        except Exception as exc:
            logger_instance.warning(f"[SYSTEM_TRAY] Failed to start tray worker thread: {exc}")
    return False


def stop_tray_icon(icon: Optional[Any]) -> bool:
    """Stops and hides the system tray icon."""
    if icon is None:
        return False
    if hasattr(icon, "stop"):
        try:
            icon.stop()
            logger_instance.info("[SYSTEM_TRAY] System tray icon stopped successfully.")
            return True
        except Exception as exc:
            logger_instance.warning(f"[SYSTEM_TRAY] Error stopping system tray icon: {exc}")
    return False
