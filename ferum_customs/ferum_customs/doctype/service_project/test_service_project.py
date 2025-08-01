import pytest
import frappe
from frappe.tests.utils import FrappeTestCase

class TestServiceProject(FrappeTestCase):
    def test_date_validation(self):
        """Test that end_date cannot be before start_date."""
        doc = frappe.new_doc("Service Project")
        doc.start_date = frappe.utils.now_datetime()
        doc.end_date = frappe.utils.add_days(doc.start_date, -1)
        
        with pytest.raises(frappe.exceptions.ValidationError):  # Use pytest for assertions
            doc.validate()

    def test_valid_date_range(self):
        """Test that valid date ranges do not raise validation errors."""
        doc = frappe.new_doc("Service Project")
        doc.start_date = frappe.utils.now_datetime()
        doc.end_date = frappe.utils.add_days(doc.start_date, 1)
        
        # This should not raise any exceptions
        doc.validate()
