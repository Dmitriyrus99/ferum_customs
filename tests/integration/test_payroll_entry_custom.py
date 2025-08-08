import frappe
from frappe.tests.utils import FrappeTestCase

from ferum_customs.ferum_customs.doctype.payroll_entry_custom.payroll_entry_custom import PayrollEntryCustom

class TestPayrollEntryCustom(FrappeTestCase):
    def test_final_amount_calculation_before_save(self):
        """Test if the final_amount is correctly calculated (salary - advance_paid)."""
        # 1. Create dependencies (Employee)
        employee = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": "Test Employee",
            "company": "_Test Company",
            "department": "_Test Department",
            "designation": "_Test Designation"
        }).insert()

        # 2. Create the PayrollEntryCustom document
        payroll_entry = frappe.get_doc({
            "doctype": "PayrollEntryCustom",
            "employee": employee.name,
            "start_date": "2025-08-01",
            "end_date": "2025-08-31",
            "salary": 100000,
            "advance_paid": 30000
        })

        # 3. Save the document, which triggers the before_save hook
        payroll_entry.save()

        # 4. Assert the result
        self.assertEqual(payroll_entry.final_amount, 70000) # 100000 - 30000

        # 5. Clean up
        payroll_entry.delete()
        employee.delete()
