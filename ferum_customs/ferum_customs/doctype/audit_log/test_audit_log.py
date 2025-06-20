import pytest

try:
	import frappe
	from frappe.tests.utils import FrappeTestCase
except Exception:  # pragma: no cover
	pytest.skip("frappe not available", allow_module_level=True)


class TestAuditLog(FrappeTestCase):
	def test_basic(self, frappe_site):
		doc = frappe.new_doc("Audit Log")
		doc.user = "Administrator"
		doc.action = "login"
		doc.insert()
		self.assertIsNotNone(doc.name)
