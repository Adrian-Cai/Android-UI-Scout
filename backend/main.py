from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .adb_manager import check_adb_available, get_default_device, list_adb_devices, validate_serial
from .device_client import input_text, press_back, tap
from .element_parser import build_element_tree, find_element_by_coordinate, parse_ui_xml
from .locator_builder import build_copy_options
from .security_guard import sanitize_text, validate_coordinate
from .snapshot_service import get_snapshot

app = FastAPI(title="Android-UI-Scout")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
_last_snapshot: dict | None = None

class SerialRequest(BaseModel):
    serial: str | None = None
class CoordinateRequest(BaseModel):
    x: float; y: float; display_width: float; display_height: float; screen_width: int; screen_height: int; serial: str | None = None
class NodeRequest(BaseModel):
    node_id: str
class TapRequest(BaseModel):
    x: int; y: int; serial: str | None = None
class InputRequest(BaseModel):
    text: str; serial: str | None = None

def _handle(fn):
    try:
        return fn()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

def _detail(element: dict | None, real_x: int | None = None, real_y: int | None = None) -> dict:
    return {"element": element, "real_x": real_x, "real_y": real_y, "code": build_copy_options(element)}

@app.get("/api/health")
def health():
    return {"status": "ok", "adb_available": check_adb_available(), "host": "127.0.0.1"}

@app.get("/api/devices")
def devices():
    return _handle(lambda: {"devices": list_adb_devices()})

@app.post("/api/connect")
def connect(req: SerialRequest):
    def run():
        serial = validate_serial(req.serial) if req.serial else get_default_device()["serial"]
        return {"serial": serial, "connected": True}
    return _handle(run)

@app.get("/api/snapshot")
def snapshot(serial: str | None = None):
    def run():
        global _last_snapshot
        _last_snapshot = get_snapshot(serial)
        return _last_snapshot
    return _handle(run)

@app.post("/api/select-by-coordinate")
def select_by_coordinate(req: CoordinateRequest):
    def run():
        if req.display_width <= 0 or req.display_height <= 0:
            raise ValueError("display size must be positive")
        real_x = int(round(req.x * req.screen_width / req.display_width))
        real_y = int(round(req.y * req.screen_height / req.display_height))
        real_x, real_y = validate_coordinate(real_x, real_y)
        snap = _last_snapshot or get_snapshot(req.serial)
        element = find_element_by_coordinate(snap.get("elements", []), real_x, real_y)
        return _detail(element, real_x, real_y)
    return _handle(run)

@app.post("/api/select-by-node")
def select_by_node(req: NodeRequest):
    def run():
        snap = _last_snapshot or get_snapshot(None)
        element = next((e for e in snap.get("elements", []) if e.get("node_id") == req.node_id), None)
        if not element:
            raise ValueError("node_id not found")
        return _detail(element)
    return _handle(run)

@app.post("/api/tap")
def api_tap(req: TapRequest):
    return _handle(lambda: tap(req.x, req.y, req.serial))

@app.post("/api/input")
def api_input(req: InputRequest):
    return _handle(lambda: input_text(sanitize_text(req.text), req.serial))

@app.post("/api/back")
def api_back(req: SerialRequest):
    return _handle(lambda: press_back(req.serial))
