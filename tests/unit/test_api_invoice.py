import importlib
from types import SimpleNamespace
import pytest

@pytest.mark.unit
def test_create_invoice_from_report(frappe_stub):
    api = importlib.reload(importlib.import_module("ferum_customs.api"))

    sr_doc = SimpleNamespace(
        get=lambda key, default=None: {
            "customer": "Cust1",
            "work_items": [
                {"description": "Work", "quantity": 2, "unit_price": 50, "amount": 100}
            ],
        }.get(key, default),
        calculate_totals=lambda: None,
    )

    items: list = []  # Added type hint for clarity
    invoice_doc = SimpleNamespace(
        name="INV001",
        append=lambda field, item: items.append(item),
        insert=lambda ignore_permissions: None,  # Placeholder for insert logic
    )

    def get_doc(doctype, name=None):
        if isinstance(doctype, dict):
            return invoice_doc
        if doctype == "Service Report":
            assert name == "SR1"
            return sr_doc
        raise AssertionError("unexpected doctype")

    frappe_stub.get_doc = get_doc
    frappe_stub.db.exists = lambda *a, **k: False  # Mocking database existence check

    result = api.create_invoice_from_report("SR1")
    assert result == "INV001"
    assert items and items[0]["description"] == "Work"
    assert len(items) == 1  # Ensure only one item is appended
    # Additional assertions can be added here to verify the invoice details
