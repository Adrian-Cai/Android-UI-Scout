"""ADB discovery and device selection."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict

_SERIAL_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")
REQUESTED_SERIAL_ENV = "ANDROID_UI_SCOUT_SERIAL"


@dataclass
class AdbDevice:
    serial: str
    status: str
    available: bool
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def check_adb_available() -> bool:
    return shutil.which("adb") is not None


def validate_serial(serial: str) -> str:
    if not serial or not _SERIAL_RE.fullmatch(serial):
        raise ValueError("invalid adb serial; allowed: letters, digits, _, -, ., :")
    return serial


def get_requested_serial() -> str | None:
    serial = os.environ.get(REQUESTED_SERIAL_ENV)
    return validate_serial(serial) if serial else None


def list_adb_devices() -> list[dict]:
    if not check_adb_available():
        raise RuntimeError("adb not found. Install Android Platform Tools and add adb to PATH.")
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "adb devices failed").strip())
    devices: list[dict] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            serial, status = parts[0], parts[1]
            msg = {"device": "ready", "unauthorized": "authorize USB debugging on device", "offline": "device is offline"}.get(status, status)
            devices.append(AdbDevice(serial, status, status == "device", msg).to_dict())
    return devices


def select_device(serial: str | None = None) -> dict:
    requested_serial = validate_serial(serial) if serial else get_requested_serial()
    devices = list_adb_devices()
    ready = [d for d in devices if d["status"] == "device"]
    if requested_serial:
        requested = next((d for d in devices if d["serial"] == requested_serial), None)
        if not requested:
            raise RuntimeError(f"requested adb serial not found: {requested_serial}")
        if requested["status"] != "device":
            raise RuntimeError(f"requested adb serial is not ready: {requested_serial}={requested['status']}")
        return requested
    if ready:
        return ready[0]
    if not devices:
        raise RuntimeError("no adb devices found. Connect a phone and enable USB debugging.")
    problems = ", ".join(f"{d['serial']}={d['status']}" for d in devices)
    raise RuntimeError(f"no available adb device: {problems}")


def get_default_device() -> dict:
    return select_device()
