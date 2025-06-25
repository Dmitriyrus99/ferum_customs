import importlib
import types
from types import SimpleNamespace

import pytest


def test_validate_duplicate_serial(frappe_stub):
    frappe_stub.db.exists = lambda doctype, filters: "SO-0002"
    captured = {}
    def throw(msg, exc=None, *a, **k):
        captured['msg'] = msg
        raise frappe_stub.ValidationError(msg)
    frappe_stub.throw = throw

    hooks = importlib.import_module("ferum_customs.custom_logic.service_object_hooks")

    doc = SimpleNamespace(serial_no=" SN123 ", name="SO-0001", get=lambda k, d=None: getattr(doc, k, d))
    with pytest.raises(frappe_stub.ValidationError):
        hooks.validate(doc)
    assert "Серийный номер" in captured['msg']
