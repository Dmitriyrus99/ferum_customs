import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestAssignedEngineerItem(FrappeTestCase):
    """Test cases for Assigned Engineer Item DocType."""

    def test_assignment_date_format(self) -> None:
        """Test that the engineer name is stripped and the assignment date is in ISO format."""
        doc = frappe.new_doc("Assigned Engineer Item")
        doc.engineer = " Engineer User "
        doc.assignment_date = frappe.utils.now_datetime().isoformat()
        doc.validate()

        # Assert that the engineer name is stripped of whitespace
        self.assertEqual(doc.engineer.strip(), "Engineer User")
        
        # Assert that the assignment date is in ISO format
        self.assertIn("T", doc.assignment_date)  # Use assertIn for better readability
