import re
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append(str(Path(__file__).resolve().parents[4]))

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase

    from ferum_customs.custom_logic import service_report_hooks
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestServiceReport(FrappeTestCase):
    def test_basic(self, frappe_site: str) -> None:
        """Test the basic functionality of the Service Report DocType."""
        doc: Any = frappe.new_doc("Service Report")
        doc.service_request = frappe.get_env("SERVICE_REQUEST", "TEST123").strip()
        doc.customer = frappe.get_env("CUSTOMER", "CUSTOMER1").strip()
        doc.posting_date = frappe.utils.now_datetime()
        doc.append(
            "work_items",
            {
                "description": "Test work item".strip(),
                "quantity": round(2.555, 2),
                "unit_price": round(100.555, 2),
            },
        )
        doc.validate()

        # Validate posting date format
        self.assertTrue(
            doc.posting_date.endswith("Z")
            or re.match(r".*\+\d{2}:\d{2}", doc.posting_date.isoformat())
        )

        # Validate work items
        for item in doc.work_items:
            self.assertEqual(item.description, "Test work item")
            self.assertAlmostEqual(item.quantity, 2.56, places=2)
            self.assertAlmostEqual(item.unit_price, 100.56, places=2)
            self.assertAlmostEqual(
                item.amount, item.quantity * item.unit_price, places=2
            )

    def test_calculate_total_payable_hook(self, frappe_site: str) -> None:
        doc: Any = frappe.new_doc("Service Report")
        doc.service_request = "SR-1"
        doc.customer = "CUSTOMER1"
        doc.posting_date = frappe.utils.now_datetime()
        doc.append(
            "work_items",
            {"description": "Item", "quantity": 2, "unit_price": 10},
        )
        service_report_hooks.calculate_total_payable(doc)
        assert doc.total_payable == 20
        assert doc.total_quantity == 2

    def test_close_related_request(self, monkeypatch: pytest.MonkeyPatch) -> None:
        doc: Any = frappe.new_doc("Service Report")
        doc.service_request = "REQ-123"

        called: dict[str, tuple[str, str, str, str]] = {}

        def fake_set_value(doctype: str, name: str, field: str, value: str) -> None:
            called["args"] = (doctype, name, field, value)

        monkeypatch.setattr(frappe.db, "set_value", fake_set_value)
        service_report_hooks.close_related_request(doc)

        assert called["args"] == (
            "Service Request",
            "REQ-123",
            "status",
            "Closed",
        )
