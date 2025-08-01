import importlib
from types import SimpleNamespace
from typing import Dict

import pytest


def test_validate_duplicate_serial(frappe_stub) -> None:
    """Test validation of duplicate serial numbers in service object."""
    
    # Mock the database check for existing serial numbers
    def mock_exists(doctype: str, filters: Dict[str, str]) -> bool:
        return filters.get("serial_no") == "SN123"
    
    frappe_stub.db.exists = mock_exists
    captured: Dict[str, str] = {}

    def throw(msg: str, exc: Exception | None = None) -> None:
        captured["msg"] = msg
        raise frappe_stub.ValidationError(msg)

    frappe_stub.throw = throw

    hooks = importlib.import_module("ferum_customs.custom_logic.service_object_hooks")

    # Create a mock document with a serial number
    doc: SimpleNamespace = SimpleNamespace(serial_no="SN123", name="SO-0001")
    doc.get = lambda k, d=None: getattr(doc, k, d)
    
    with pytest.raises(frappe_stub.ValidationError):
        hooks.validate(doc)
    
    assert "Серийный номер" in captured["msg"]
