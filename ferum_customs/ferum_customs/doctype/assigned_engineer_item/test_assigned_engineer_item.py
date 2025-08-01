import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestAssignedEngineerItem(FrappeTestCase):
    def test_assignment_date_format(self):
        doc = frappe.new_doc("Assigned Engineer Item")
        doc.engineer = " Engineer User "
        doc.assignment_date = frappe.utils.now_datetime().isoformat()
        doc.validate()
        self.assertEqual(doc.engineer.strip(), "Engineer User")
        self.assertIn("T", doc.assignment_date)  # Use assertIn for better readability
