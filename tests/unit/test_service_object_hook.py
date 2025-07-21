import importlib
import types
from types import SimpleNamespace

import pytest


from typing import Any


def test_validate_duplicate_serial(frappe_stub) -> None:
    frappe_stub.db.exists = lambda doctype, filters: "SO-0002"
    captured: dict[str, str] = {}

    def throw(msg: str, exc: Exception | None = None, *a: Any, **k: Any) -> None:
        captured["msg"] = msg
        raise frappe_stub.ValidationError(msg)

    frappe_stub.throw = throw

    hooks = importlib.import_module("ferum_customs.custom_logic.service_object_hooks")

    doc: SimpleNamespace = SimpleNamespace(serial_no=" SN123 ", name="SO-0001")
    doc.get = lambda k, d=None: getattr(doc, k, d)
    with pytest.raises(frappe_stub.ValidationError):
        hooks.validate(doc)
    assert "Серийный номер" in captured["msg"]
