import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestCustomAttachment(FrappeTestCase):
    """Test cases for the Custom Attachment DocType."""

    def test_basic(self) -> None:
        """Test basic functionality of Custom Attachment."""
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = "Photo"  # Normalize input
        doc.attachment_file = "/path/to/file.jpg"  # Normalize input
        doc.validate()
        self.assertEqual(doc.attachment_type, "photo")
        self.assertEqual(doc.attachment_file, "/path/to/file.jpg")

    def test_invalid_attachment_file(self) -> None:
        """Test validation for invalid attachment file."""
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = "Photo"
        doc.attachment_file = ""  # Invalid input
        with self.assertRaises(frappe.ValidationError):
            doc.validate()
