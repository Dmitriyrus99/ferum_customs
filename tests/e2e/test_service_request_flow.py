import pytest

frappe = pytest.importorskip("frappe")
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api
from ferum_customs.constants import STATUS_OTKRYTA


@pytest.mark.slow
class TestServiceRequestFlow(FrappeTestCase):
    def test_full_flow(self, frappe_site):
        # Ensure the service request is created successfully
        sr_name = api.bot_create_service_request("E2E Subject")
        self.assertIsNotNone(sr_name, "Service request creation failed, returned None")
        
        # Check if the service request exists in the database
        self.assertTrue(frappe.db.exists("Service Request", sr_name), f"Service Request {sr_name} does not exist in the database")
        
        # Retrieve open service requests and check if the created request is among them
        open_requests = api.bot_get_service_requests(status=STATUS_OTKRYTA)
        names = [r["name"] for r in open_requests]
        self.assertIn(sr_name, names, f"Service Request {sr_name} not found in open requests")
