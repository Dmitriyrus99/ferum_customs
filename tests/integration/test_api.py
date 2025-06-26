import pytest

frappe = pytest.importorskip("frappe")
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api


class TestAPIIntegration(FrappeTestCase):
	def test_bot_create_and_get_service_request(self, frappe_site):
		name = api.bot_create_service_request("From bot", description="demo")
		self.assertTrue(frappe.db.exists("Service Request", name))
		results = api.bot_get_service_requests()
		self.assertIn(name, [r["name"] for r in results])
