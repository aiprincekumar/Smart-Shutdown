# -*- coding: utf-8 -*-
"""
core.settings_store: Atomic UTF-8 BOM JSON settings persistence and .bak recovery.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

_LOGGER_NAME = "SmartShutdown"


def get_backup_path(primary: Path) -> Path:
    """Return the paired backup path (`<name>.bak`) for a settings file."""
    target = Path(primary)
    return target.with_name(f"{target.name}.bak")


def _serialize_json_dict(data: Dict[str, Any]) -> str:
    """Serialize a dictionary as formatted JSON with a trailing newline."""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _remove_temp_file(tmp_name: Optional[str]) -> None:
    """Remove an orphaned temporary file if present."""
    if not tmp_name:
        return
    try:
        Path(tmp_name).unlink(missing_ok=True)
    except OSError:
        pass


def _replace_with_retry(src: str, dst: str, retries: int = 3) -> None:
    """Atomically replace destination path with brief Windows lock retry."""
    for attempt in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if attempt >= retries - 1:
                raise
            time.sleep(0.03 * (attempt + 1))


def read_json_dict(path: Path, logger: Optional[logging.Logger] = None) -> Optional[Dict[str, Any]]:
    """Read and validate a JSON object dictionary from UTF-8 BOM file."""
    target = Path(path)
    if not target.exists():
        return None
    log = logger or logging.getLogger(_LOGGER_NAME)
    try:
        data = json.loads(target.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        log.warning(f"[CONFIG] Failed reading settings JSON {target}: {exc}")
        return None
    if isinstance(data, dict):
        return data
    log.warning(f"[CONFIG] Ignoring non-dict settings JSON in {target}")
    return None


def atomic_write_text(path: Path, content: str) -> None:
    """Atomically write UTF-8 BOM text using tempfile, fsync, and os.replace."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_name: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", dir=str(target.parent),
            prefix=f".{target.stem}_", suffix=".tmp", delete=False, newline="\n",
        ) as handle:
            tmp_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(tmp_name, str(target))
    except Exception:
        _remove_temp_file(tmp_name)
        raise


def save_json_dict_atomic(
    path: Path, data: Dict[str, Any], logger: Optional[logging.Logger] = None
) -> bool:
    """Persist JSON dict atomically with two-phase .bak preservation and sync."""
    target = Path(path)
    log = logger or logging.getLogger(_LOGGER_NAME)
    bak_path = get_backup_path(target)
    try:
        payload = _serialize_json_dict(data)
        if target.exists() and not bak_path.exists():
            prev_data = read_json_dict(target, logger=log)
            if prev_data is not None:
                atomic_write_text(bak_path, _serialize_json_dict(prev_data))
        atomic_write_text(target, payload)
        atomic_write_text(bak_path, payload)
        return True
    except Exception as exc:
        log.warning(f"[CONFIG] Failed saving {target}: {exc}")
        return False


def _recover_from_backup(primary: Path, log: logging.Logger) -> Optional[Dict[str, Any]]:
    """Recover settings dictionary from paired .bak and self-heal primary file."""
    bak_path = get_backup_path(primary)
    if not bak_path.exists():
        return None
    bak_data = read_json_dict(bak_path, logger=log)
    if bak_data is None:
        return None
    log.warning(f"[CONFIG] Recovered settings from backup {bak_path}")
    try:
        atomic_write_text(primary, _serialize_json_dict(bak_data))
    except Exception as exc:
        log.warning(f"[CONFIG] Failed self-healing {primary} from backup: {exc}")
    return bak_data


def load_settings_dict(
    primary: Path,
    legacy: Optional[Path] = None,
    allow_legacy: bool = False,
    logger: Optional[logging.Logger] = None,
) -> Optional[Dict[str, Any]]:
    """Load settings dict from primary JSON, .bak recovery, or legacy fallback."""
    target = Path(primary)
    log = logger or logging.getLogger(_LOGGER_NAME)
    data = read_json_dict(target, logger=log)
    if data is not None:
        return data
    recovered = _recover_from_backup(target, log)
    if recovered is not None:
        return recovered
    if allow_legacy and legacy is not None:
        legacy_target = Path(legacy)
        if legacy_target.exists():
            return read_json_dict(legacy_target, logger=log)
    return None
