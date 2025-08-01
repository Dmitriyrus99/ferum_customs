import pytest
from frappe import new_doc, utils, exceptions
from frappe.tests.utils import FrappeTestCase

class TestServiceProject(FrappeTestCase):
    def test_date_validation(self):
        """Test that end_date cannot be before start_date."""
        doc = new_doc("Service Project")
        doc.start_date = utils.now_datetime()
        doc.end_date = utils.add_days(doc.start_date, -1)
        
        with pytest.raises(exceptions.ValidationError):
            doc.validate()

    def test_valid_date_range(self):
        """Test that valid date ranges do not raise validation errors."""
        doc = new_doc("Service Project")
        doc.start_date = utils.now_datetime()
        doc.end_date = utils.add_days(doc.start_date, 1)
        
        # This should not raise any exceptions
        doc.validate()  # Ensure that no exceptions are raised
