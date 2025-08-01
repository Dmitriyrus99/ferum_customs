import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestPayrollEntryCustom(FrappeTestCase):
    def test_total_payable_rounding(self):
        doc = frappe.new_doc("Payroll Entry Custom")
        doc.total_payable = 1234.567
        doc.validate()
        self.assertAlmostEqual(doc.total_payable, 1234.57, places=2)

# Issues:
# 1. The test assumes that `doc.validate()` will round `total_payable`, but this behavior should be explicitly defined in the `validate` method of the `Payroll Entry Custom` doctype.
# 2. The test does not check if the `validate` method is correctly implemented to handle rounding. Ensure that the `validate` method in the doctype is responsible for rounding.
# 3. The test should include setup and teardown methods if there are any dependencies or side effects.
# 4. Consider adding more test cases to cover edge cases and different scenarios for rounding.
