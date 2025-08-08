import frappe
from frappe.tests.utils import FrappeTestCase

class TestServiceRequestFlow(FrappeTestCase):
    def setUp(self):
        self.customer = frappe.get_doc({"doctype": "Customer", "customer_name": "_Test Customer"}).insert()
        self.service_object = frappe.get_doc({
            "doctype": "ServiceObject",
            "object_name": "Test Object for Flow",
            "customer": self.customer.name
        }).insert()

    def tearDown(self):
        # Clean up any remaining documents
        frappe.db.rollback()

    def test_prevent_deletion_of_service_object_with_active_request(self):
        """Test that a ServiceObject with an active ServiceRequest cannot be deleted."""
        service_request = frappe.get_doc({
            "doctype": "ServiceRequest",
            "subject": "Active Request Test",
            "status": "Open",
            "service_object": self.service_object.name
        }).insert()

        # Attempting to delete the ServiceObject should raise an exception
        self.assertRaises(frappe.ValidationError, self.service_object.delete)

        # Clean up
        service_request.delete()

    def test_prevent_closing_service_request_without_report(self):
        """Test that a ServiceRequest cannot be closed without a linked ServiceReport."""
        service_request = frappe.get_doc({
            "doctype": "ServiceRequest",
            "subject": "Close Request Test",
            "status": "Open",
            "service_object": self.service_object.name
        }).insert()

        service_request.status = "Closed"
        # Attempting to save with status "Closed" should fail
        self.assertRaises(frappe.ValidationError, service_request.save)

        # Clean up
        service_request.delete()
