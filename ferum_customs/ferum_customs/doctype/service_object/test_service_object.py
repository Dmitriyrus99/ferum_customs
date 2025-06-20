import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except Exception:  # pragma: no cover
    pytest.skip("frappe not available", allow_module_level=True)


class TestServiceObject(FrappeTestCase):
    def test_description_trim(self, frappe_site):
        doc = frappe.new_doc("Service Object")
        doc.linked_service_project = " PROJECT001 "
        doc.validate()
        self.assertEqual(doc.linked_service_project, "PROJECT001")
