"""Parse Android hierarchy XML into selectable UI elements."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

_BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")


def parse_bounds(bounds_str: str) -> dict | None:
    match = _BOUNDS_RE.fullmatch(bounds_str or "")
    if not match:
        return None
    left, top, right, bottom = map(int, match.groups())
    width, height = max(0, right - left), max(0, bottom - top)
    return {"left": left, "top": top, "right": right, "bottom": bottom, "width": width, "height": height,
            "center_x": left + width // 2, "center_y": top + height // 2}


def _bool(v: str | None) -> bool:
    return str(v).lower() == "true"


def parse_ui_xml(xml: str) -> list[dict]:
    if not xml:
        return []
    root = ET.fromstring(xml)
    elements: list[dict] = []

    def walk(node: ET.Element, parent_id: str | None) -> None:
        if node.tag == "node":
            node_id = str(len(elements))
            element = {
                "node_id": node_id, "parent_id": parent_id, "index": node.attrib.get("index", ""),
                "text": node.attrib.get("text", ""), "resource_id": node.attrib.get("resource-id", ""),
                "content_desc": node.attrib.get("content-desc", ""), "class_name": node.attrib.get("class", ""),
                "package": node.attrib.get("package", ""), "bounds": parse_bounds(node.attrib.get("bounds", "")),
                "clickable": _bool(node.attrib.get("clickable")), "enabled": _bool(node.attrib.get("enabled")),
                "selected": _bool(node.attrib.get("selected")), "focused": _bool(node.attrib.get("focused")),
                "scrollable": _bool(node.attrib.get("scrollable")), "children": [],
            }
            elements.append(element)
            parent_id = node_id
        for child in list(node):
            walk(child, parent_id)

    walk(root, None)
    return elements


def find_element_by_coordinate(elements: list[dict], x: int, y: int) -> dict | None:
    hits = []
    for el in elements:
        b = el.get("bounds")
        if b and b["left"] <= x <= b["right"] and b["top"] <= y <= b["bottom"]:
            area = b["width"] * b["height"]
            meaningful = bool(el.get("resource_id") or el.get("text") or el.get("content_desc"))
            hits.append((area, not meaningful, el))
    if not hits:
        return None
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits[0][2]


def build_element_tree(elements: list[dict]) -> list[dict]:
    by_id = {el["node_id"]: {**el, "children": []} for el in elements}
    roots = []
    for el in by_id.values():
        parent_id = el.get("parent_id")
        if parent_id is not None and parent_id in by_id:
            by_id[parent_id]["children"].append(el)
        else:
            roots.append(el)
    return roots
