from __future__ import annotations

from .adb_manager import get_default_device, validate_serial
from .device_client import dump_hierarchy, get_screen_size, screenshot
from .element_parser import build_element_tree, parse_ui_xml


def get_snapshot(serial: str | None = None) -> dict:
    serial = validate_serial(serial) if serial else get_default_device()["serial"]
    width, height = get_screen_size(serial)
    xml = dump_hierarchy(serial)
    elements = parse_ui_xml(xml)
    return {"device": {"serial": serial, "screen_width": width, "screen_height": height},
            "screenshot": screenshot(serial), "xml": xml, "elements": elements, "element_tree": build_element_tree(elements)}
