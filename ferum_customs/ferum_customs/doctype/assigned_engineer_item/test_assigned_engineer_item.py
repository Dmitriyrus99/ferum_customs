import pytest

try:
	import frappe
	from frappe.tests.utils import FrappeTestCase
except Exception:  # pragma: no cover
	pytest.skip("frappe not available", allow_module_level=True)


class TestAssignedEngineerItem(FrappeTestCase):
	def test_assignment_date_format(self, frappe_site):
		doc = frappe.new_doc("Assigned Engineer Item")
		doc.engineer = " Engineer User "
		doc.assignment_date = frappe.utils.now_datetime()
		doc.validate()
		self.assertEqual(doc.engineer, "Engineer User")
		self.assertTrue("T" in doc.assignment_date)  # ISO 8601 check
