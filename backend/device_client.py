"""uiautomator2 device wrapper."""
from __future__ import annotations

import base64
import io

from .adb_manager import get_default_device, validate_serial
from .security_guard import sanitize_text, validate_coordinate


def _u2():
    try:
        import uiautomator2 as u2
        return u2
    except Exception as exc:
        raise RuntimeError(f"uiautomator2 import failed: {exc}") from exc


def _serial(serial: str | None) -> str:
    return validate_serial(serial) if serial else get_default_device()["serial"]


def connect_device(serial: str | None = None):
    s = _serial(serial)
    try:
        return _u2().connect(s)
    except Exception as exc:
        raise RuntimeError(f"failed to connect device {s}: {exc}") from exc


def get_device_info(serial: str | None = None) -> dict:
    d = connect_device(serial)
    return dict(d.info)


def get_screen_size(serial: str | None = None) -> tuple[int, int]:
    d = connect_device(serial)
    try:
        return tuple(d.window_size())
    except Exception:
        info = d.info
        return int(info.get("displayWidth", 0)), int(info.get("displayHeight", 0))


def screenshot(serial: str | None = None) -> str:
    d = connect_device(serial)
    try:
        image = d.screenshot()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as exc:
        raise RuntimeError(f"failed to capture screenshot: {exc}") from exc


def dump_hierarchy(serial: str | None = None) -> str:
    try:
        return connect_device(serial).dump_hierarchy()
    except Exception as exc:
        raise RuntimeError(f"failed to dump UI hierarchy: {exc}") from exc


def tap(x, y, serial: str | None = None) -> dict:
    x, y = validate_coordinate(x, y)
    connect_device(serial).click(x, y)
    return {"ok": True, "x": x, "y": y}


def input_text(text: str, serial: str | None = None) -> dict:
    value = sanitize_text(text)
    connect_device(serial).send_keys(value, clear=False)
    return {"ok": True, "text": value}


def press_back(serial: str | None = None) -> dict:
    connect_device(serial).press("back")
    return {"ok": True}
