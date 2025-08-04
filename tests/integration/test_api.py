import pytest

frappe = pytest.importorskip("frappe")
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api


class TestAPIIntegration(FrappeTestCase):
    def test_bot_create_and_get_service_request(self) -> None:
        """Test the creation and retrieval of a service request by the bot."""
        # Ensure the test is isolated by using a transaction or a test site
        with self.frappe_site:
            name = api.bot_create_service_request("From bot", description="demo")
            self.assertTrue(
                frappe.db.exists("Service Request", name),
                "Service Request was not created.",
            )

            results = api.bot_get_service_requests()
            service_request_names = [r["name"] for r in results]
            self.assertIn(
                name,
                service_request_names,
                "Service Request name not found in the results.",
            )
