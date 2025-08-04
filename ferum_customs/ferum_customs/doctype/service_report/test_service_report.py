import re
from typing import Any

import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
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
