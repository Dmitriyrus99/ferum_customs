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

    def test_attachment_type_normalization(self) -> None:
        """Test normalization of attachment type."""
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = "VIDEO"
        doc.validate()
        self.assertEqual(doc.attachment_type, "video")

    def test_attachment_file_path_sanitization(self) -> None:
        """Test sanitization of attachment file path."""
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = "Photo"
        doc.attachment_file = "../../etc/passwd"  # Potentially unsafe input
        with self.assertRaises(frappe.ValidationError):
            doc.validate()
