"""Local-only service validation helpers."""
from __future__ import annotations

import re

_ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def validate_host(host: str) -> str:
    if host not in _ALLOWED_HOSTS:
        raise ValueError("Android-UI-Scout only listens on 127.0.0.1/localhost")
    return "127.0.0.1" if host == "localhost" else host


def validate_port(port: int) -> int:
    if not isinstance(port, int) or port < 1024 or port > 65535:
        raise ValueError("port must be an integer between 1024 and 65535")
    return port


def validate_coordinate(x: int | float, y: int | float) -> tuple[int, int]:
    try:
        ix, iy = int(round(float(x))), int(round(float(y)))
    except (TypeError, ValueError) as exc:
        raise ValueError("coordinate must be numeric") from exc
    if ix < 0 or iy < 0:
        raise ValueError("coordinate must be non-negative")
    return ix, iy


def sanitize_text(text: str) -> str:
    if text is None:
        return ""
    cleaned = _CONTROL_CHARS.sub("", str(text)).replace("\r", " ").replace("\n", " ")
    return cleaned[:1000]
