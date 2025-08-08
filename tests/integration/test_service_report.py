import frappe
from frappe.tests.utils import FrappeTestCase

class TestServiceReport(FrappeTestCase):
    def setUp(self):
        self.customer = frappe.get_doc({"doctype": "Customer", "customer_name": "_Test Customer"}).insert()
        self.service_object = frappe.get_doc({
            "doctype": "ServiceObject",
            "object_name": "Test Object for Report",
            "customer": self.customer.name
        }).insert()
        self.service_request = frappe.get_doc({
            "doctype": "ServiceRequest",
            "subject": "Report Test Request",
            "status": "Open",
            "service_object": self.service_object.name
        }).insert()

    def tearDown(self):
        frappe.db.rollback()

    def test_service_request_status_update_on_submit(self):
        """Test that submitting a ServiceReport closes the linked ServiceRequest."""
        service_report = frappe.get_doc({
            "doctype": "ServiceReport",
            "service_request": self.service_request.name,
            "date": frappe.utils.nowdate()
        }).insert()

        service_report.submit()

        updated_request = frappe.get_doc("ServiceRequest", self.service_request.name)
        self.assertEqual(updated_request.status, "Closed")

    def test_total_cost_calculation(self):
        """Test that the total_cost in ServiceReport is calculated correctly."""
        service_report = frappe.get_doc({
            "doctype": "ServiceReport",
            "service_request": self.service_request.name,
            "date": frappe.utils.nowdate()
        })
        service_report.append("work_items", {
            "description": "Task 1", "quantity": 2, "cost": 1000
        })
        service_report.append("work_items", {
            "description": "Task 2", "quantity": 1, "cost": 500
        })
        service_report.insert()

        self.assertEqual(service_report.total_cost, 2500) # (2 * 1000) + (1 * 500)
