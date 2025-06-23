import pytest

try:
	import frappe
	from frappe.tests.utils import FrappeTestCase
except Exception:  # pragma: no cover
	pytest.skip("frappe not available", allow_module_level=True)


class TestPayrollEntryCustom(FrappeTestCase):
	def test_total_payable_rounding(self, frappe_site):
		doc = frappe.new_doc("Payroll Entry Custom")
		doc.total_payable = 1234.567
		doc.validate()
		self.assertAlmostEqual(doc.total_payable, 1234.57, places=2)
