"""Build uiautomator2 locators and code snippets."""
from __future__ import annotations


def _q(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace('"', '\\"')


def build_xpath(element: dict | None) -> str:
    if not element:
        return ""
    if element.get("resource_id"):
        return f'//*[@resource-id="{_q(element["resource_id"])}"]'
    if element.get("content_desc"):
        return f'//*[@content-desc="{_q(element["content_desc"])}"]'
    if element.get("text"):
        return f'//*[@text="{_q(element["text"])}"]'
    cls = element.get("class_name") or "*"
    return f'//{cls}' if cls != "*" else "//*"


def build_locator(element: dict | None) -> dict:
    if not element:
        return {"recommended_locator": "", "stability": "none"}
    rid, desc, text, cls = element.get("resource_id"), element.get("content_desc"), element.get("text"), element.get("class_name")
    if rid:
        return {"recommended_locator": f'd(resourceId="{_q(rid)}")', "stability": "high"}
    if desc:
        return {"recommended_locator": f'd(description="{_q(desc)}")', "stability": "high"}
    if text:
        return {"recommended_locator": f'd(text="{_q(text)}")', "stability": "medium"}
    if cls and text:
        return {"recommended_locator": f'd(className="{_q(cls)}", text="{_q(text)}")', "stability": "medium"}
    if cls and element.get("clickable"):
        return {"recommended_locator": f'd(className="{_q(cls)}", clickable=True)', "stability": "low"}
    return {"recommended_locator": f'd.xpath("{_q(build_xpath(element))}")', "stability": "low"}


def build_click_code(element: dict | None) -> str:
    loc = build_locator(element)["recommended_locator"]
    if loc:
        return f"{loc}.click()"
    b = (element or {}).get("bounds") or {}
    return f"d.click({b.get('center_x', 0)}, {b.get('center_y', 0)})"


def build_copy_options(element: dict | None) -> dict:
    b = (element or {}).get("bounds") or {}
    loc = build_locator(element)
    return {**loc, "click_code": build_click_code(element), "xpath": build_xpath(element),
            "coordinate_code": f"d.click({b.get('center_x', 0)}, {b.get('center_y', 0)})"}
