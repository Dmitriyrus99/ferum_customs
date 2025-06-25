import pytest

frappe = pytest.importorskip("frappe")
from frappe.tests.utils import FrappeTestCase

from ferum_customs import api
from ferum_customs.constants import STATUS_OTKRYTA


@pytest.mark.slow
class TestServiceRequestFlow(FrappeTestCase):
	def test_full_flow(self, frappe_site):
		sr_name = api.bot_create_service_request("E2E Subject")
		self.assertTrue(frappe.db.exists("Service Request", sr_name))
		open_requests = api.bot_get_service_requests(status=STATUS_OTKRYTA)
		names = [r["name"] for r in open_requests]
		self.assertIn(sr_name, names)
