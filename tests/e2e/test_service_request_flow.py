import pytest
from frappe import db
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api
from ferum_customs.constants import STATUS_OTKRYTA


@pytest.mark.slow
class TestServiceRequestFlow(FrappeTestCase):
    """Test the full flow of service request creation and retrieval."""

    def test_full_flow(self, frappe_site: str) -> None:
        """Test the complete service request flow from creation to retrieval."""

        # Ensure the service request is created successfully
        sr_name = api.bot_create_service_request("E2E Subject")
        self.assertIsNotNone(sr_name, "Service request creation failed, returned None")

        # Check if the service request exists in the database
        self.assertTrue(
            db.exists("Service Request", sr_name),
            f"Service Request {sr_name} does not exist in the database",
        )

        # Retrieve open service requests and check if the created request is among them
        open_requests = api.bot_get_service_requests(status=STATUS_OTKRYTA)
        names = [r["name"] for r in open_requests]
        self.assertIn(
            sr_name, names, f"Service Request {sr_name} not found in open requests"
        )
