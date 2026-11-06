"""Validate and serialize TkForge project documents without a GUI.

Only persist the documented widget fields. Never trust arbitrary JSON objects
to become live GUI state or generated Python identifiers.
"""
import re

MAX_WIDGETS = 300
MAX_FILE_BYTES = 2_000_000
WIDGET_TYPES = frozenset({
    "button", "label", "entry", "text", "checkbutton", "radiobutton",
    "listbox", "combobox", "frame", "canvas"
})
_ID = re.compile(r"^(button|label|entry|text|checkbutton|radiobutton|listbox|combobox|frame|canvas)_[1-9][0-9]*$")
_FIELDS = ("id", "type", "name", "x", "y", "width", "height",
           "text", "bg", "fg", "font")


def _check_text(value, field, limit=500):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f"{field} must be a string up to {limit} characters")
    return value


def validate_project(data):
    """Return a sanitized, independent list of widgets or raise ValueError.

    No GUI state is modified by this function.
    """
    if not isinstance(data, list) or len(data) > MAX_WIDGETS:
        raise ValueError(f"Project must contain at most {MAX_WIDGETS} widgets")
    validated = []
    seen = set()
    for idx, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ValueError(f"Widget {idx} must be a JSON object")
        kind = raw.get("type")
        ident = raw.get("id")
        if kind not in WIDGET_TYPES or not isinstance(ident, str):
            raise ValueError(f"Widget {idx} has invalid type or identifier")
        if not _ID.fullmatch(ident) or not ident.startswith(kind + "_"):
            raise ValueError(f"Widget {idx} has invalid identifier")
        if ident in seen:
            raise ValueError(f"Duplicate widget identifier: {ident}")
        seen.add(ident)
        clean = {"id": ident, "type": kind,
                 "name": _check_text(raw.get("name", kind.title()), "name", 80)}
        for field in ("x", "y", "width", "height"):
            value = raw.get(field)
            if type(value) is not int or not -10000 <= value <= 10000:
                raise ValueError(f"Widget {ident}: invalid {field}")
            if field in ("width", "height") and value < 1:
                raise ValueError(f"Widget {ident}: {field} must be positive")
            clean[field] = value
        for field in ("text", "bg", "fg"):
            clean[field] = _check_text(raw.get(field), field)
        font = raw.get("font", ("Arial", 10))
        if not isinstance(font, (list, tuple)) or len(font) != 2:
            raise ValueError(f"Widget {ident}: font must be a [family, size] pair")
        family, size = font
        _check_text(family, "font family", 80)
        if type(size) is not int or not 1 <= size <= 120:
            raise ValueError(f"Widget {ident}: invalid font size")
        clean["font"] = (family, size)
        clean["canvas_id"] = None
        validated.append(clean)
    return validated


def export_project(widgets):
    """Serialize only supported project fields, never canvas/event state."""
    records = []
    for widget in widgets:
        records.append({key: widget[key] for key in _FIELDS})
    # Re-run the same validation for both imported and exported project files.
    return [{key: widget[key] for key in _FIELDS}
            for widget in validate_project(records)]
