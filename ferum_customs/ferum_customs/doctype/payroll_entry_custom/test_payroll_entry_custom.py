import pytest

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)


class TestPayrollEntryCustom(FrappeTestCase):
    def setUp(self):
        # Setup code if needed
        pass

    def tearDown(self):
        # Teardown code if needed
        pass

    def test_total_payable_rounding(self):
        """Test that total_payable is rounded to two decimal places in the validate method."""
        doc = frappe.new_doc("Payroll Entry Custom")
        doc.total_payable = 1234.567
        doc.validate()  # Ensure validate method handles rounding
        self.assertAlmostEqual(doc.total_payable, 1234.57, places=2)

    def test_total_payable_rounding_edge_cases(self):
        """Test edge cases for total_payable rounding."""
        edge_cases = [1234.564, 1234.565, 1234.566]
        expected_results = [1234.56, 1234.57, 1234.57]
        
        for value, expected in zip(edge_cases, expected_results):
            doc = frappe.new_doc("Payroll Entry Custom")
            doc.total_payable = value
            doc.validate()
            self.assertAlmostEqual(doc.total_payable, expected, places=2)
