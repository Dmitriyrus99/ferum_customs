import frappe
from frappe.tests.utils import FrappeTestCase

class TestServiceProject(FrappeTestCase):
    def setUp(self):
        self.customer = frappe.get_doc({"doctype": "Customer", "customer_name": "_Test Customer"}).insert()
        self.service_object1 = frappe.get_doc({
            "doctype": "ServiceObject",
            "object_name": "Test Object 1",
            "customer": self.customer.name
        }).insert()

    def tearDown(self):
        self.service_object1.delete()
        self.customer.delete()

    def test_duplicate_service_object_validation(self):
        """Test that a ServiceProject cannot have duplicate ServiceObjects."""
        project = frappe.get_doc({
            "doctype": "ServiceProject",
            "project_name": "Test Project for Duplicates",
            "customer": self.customer.name
        })
        project.append("service_objects", {"service_object": self.service_object1.name})
        project.append("service_objects", {"service_object": self.service_object1.name}) # Add duplicate

        # Assert that saving the document raises a ValidationError
        self.assertRaises(frappe.ValidationError, project.save)
