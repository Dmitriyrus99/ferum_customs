import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestServiceObject(FrappeTestCase):
    def test_linked_service_project_trim(self) -> None:
        """Test that leading and trailing whitespace is trimmed from linked_service_project."""
        doc = frappe.new_doc("Service Object")
        doc.linked_service_project = " PROJECT001 "
        doc.validate()
        self.assertEqual(doc.linked_service_project, "PROJECT001")  # Ensure trimming is tested

    def test_linked_service_project_empty(self) -> None:
        """Test that linked_service_project can handle empty string."""
        doc = frappe.new_doc("Service Object")
        doc.linked_service_project = ""
        doc.validate()
        self.assertEqual(doc.linked_service_project, "")  # Ensure empty string is handled

    def test_linked_service_project_none(self) -> None:
        """Test that linked_service_project can handle None."""
        doc = frappe.new_doc("Service Object")
        doc.linked_service_project = None
        doc.validate()
        self.assertIsNone(doc.linked_service_project)  # Ensure None is handled
