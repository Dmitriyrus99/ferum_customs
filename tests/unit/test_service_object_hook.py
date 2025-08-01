import importlib
from types import SimpleNamespace
from typing import Any, Dict

import pytest


def test_validate_duplicate_serial(frappe_stub) -> None:
    # Use a more realistic mock for the database check
    frappe_stub.db.exists = lambda doctype, filters: filters.get("serial_no") == "SN123"
    captured: Dict[str, str] = {}

    def throw(msg: str, exc: Exception | None = None, *a: Any, **k: Any) -> None:
        captured["msg"] = msg
        raise frappe_stub.ValidationError(msg)

    frappe_stub.throw = throw

    hooks = importlib.import_module("ferum_customs.custom_logic.service_object_hooks")

    # Strip whitespace from serial_no to match realistic scenarios
    doc: SimpleNamespace = SimpleNamespace(serial_no="SN123", name="SO-0001")
    doc.get = lambda k, d=None: getattr(doc, k, d)
    
    with pytest.raises(frappe_stub.ValidationError):
        hooks.validate(doc)
    
    assert "Серийный номер" in captured["msg"]
