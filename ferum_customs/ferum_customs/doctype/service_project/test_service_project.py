import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestServiceProject(FrappeTestCase):
    def test_date_validation(self):
        doc = frappe.new_doc("Service Project")
        doc.start_date = frappe.utils.now_datetime()
        doc.end_date = frappe.utils.add_days(doc.start_date, -1)
        with self.assertRaises(frappe.exceptions.ValidationError):  # Use specific exception
            doc.validate()
