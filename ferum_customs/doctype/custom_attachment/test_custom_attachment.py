import pytest

try:
	import frappe
	from frappe.tests.utils import FrappeTestCase
except Exception:  # pragma: no cover
	pytest.skip("frappe not available", allow_module_level=True)


class TestCustomAttachment(FrappeTestCase):
	def test_basic(self, frappe_site):
		doc = frappe.new_doc("Custom Attachment")
		doc.attachment_type = " Photo "
		doc.attachment_file = " /path/to/file.jpg "
		doc.validate()
		self.assertEqual(doc.attachment_type, "photo")
		self.assertEqual(doc.attachment_file, "/path/to/file.jpg")
