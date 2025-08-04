import pytest
from frappe.exceptions import DoesNotExistError
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api


class TestAPI(FrappeTestCase):
    def test_validate_service_request(self) -> None:
        """Test validate_service_request method for valid and invalid cases."""

        # Test with a valid document name
        doc = api.validate_service_request("test_docname")
        self.assertIsNotNone(doc)
        self.assertEqual(getattr(doc, "name", None), "test_docname")

        # Test with an invalid document name
        with self.assertRaises(DoesNotExistError):
            api.validate_service_request("invalid_docname")

        # Additional tests for edge cases can be added here
