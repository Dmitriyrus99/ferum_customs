import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:  # More specific exception
    pytest.skip("frappe not available", allow_module_level=True)


class TestCustomAttachment(FrappeTestCase):
    def test_basic(self, frappe_site):
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = " Photo ".strip().lower()  # Normalize input
        doc.attachment_file = " /path/to/file.jpg ".strip()  # Normalize input
        doc.validate()
        self.assertEqual(doc.attachment_type, "photo")
        self.assertEqual(doc.attachment_file, "/path/to/file.jpg")
