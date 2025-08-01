from unittest.mock import patch
import pytest
from typing import Optional

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
    from frappe.utils import add_days, now_datetime
except ImportError:
    pytest.skip("frappe not available", allow_module_level=True)

from ferum_customs.constants import STATUS_OTKRYTA, STATUS_VYPOLNENA, STATUS_ZAKRYTA

TEST_CUSTOMER_NAME = "_Test Customer for SR Tests"
TEST_ENGINEER_USER_EMAIL = "test_sr_engineer_ferum@example.com"
TEST_PM_USER_EMAIL = "test_sr_pm_ferum@example.com"
TEST_SP_NAME_FIELD = "_Test SP for SR Tests"
ACTUAL_TEST_SP_NAME = TEST_SP_NAME_FIELD
ACTUAL_TEST_SO_NAME = "_Test SO for SR Tests"

class TestServiceRequest(FrappeTestCase):
    test_customer_name: str = TEST_CUSTOMER_NAME
    test_engineer_user_email: str = TEST_ENGINEER_USER_EMAIL
    test_pm_user_email: str = TEST_PM_USER_EMAIL
    test_sp_name_field: str = TEST_SP_NAME_FIELD
    actual_test_sp_name: str = ACTUAL_TEST_SP_NAME
    actual_test_so_name: str = ACTUAL_TEST_SO_NAME

    def setUp(self) -> None:
        frappe.db.savepoint()
        self.current_user_for_test = frappe.session.user
        frappe.set_user(self.test_pm_user_email)

    def tearDown(self) -> None:
        frappe.set_user(self.current_user_for_test)
        frappe.db.rollback()

    def create_service_request_doc(self, status: str = STATUS_OTKRYTA, submit_doc: bool = False) -> Optional[frappe.Document]:
        """Create a Service Request document with the given status."""
        sr = frappe.new_doc("Service Request")
        sr.subject = "Test SR - " + frappe.generate_hash(length=5)
        sr.custom_customer = self.test_customer_name
        sr.custom_service_object_link = self.actual_test_so_name
        sr.request_datetime = now_datetime()
        sr.status = status
        sr.insert(ignore_permissions=True)
        if submit_doc and sr.docstatus == 0:
            try:
                sr.submit()
            except frappe.exceptions.DoesNotExistError as e:
                if "WorkflowState" in str(e) and "Открыта" in str(e):
                    frappe.get_doc("Workflow State", {"workflow_state_name": "Открыта"}).save(ignore_permissions=True)
                    sr.reload()
                    sr.submit()
                else:
                    raise
        return sr

    def test_sr_creation_and_custom_fields(self, frappe_site) -> None:
        """Test creation of Service Request and custom fields."""
        sr = self.create_service_request_doc()
        self.assertEqual(sr.custom_customer, self.test_customer_name)
        self.assertEqual(sr.custom_service_object_link, self.actual_test_so_name)

        fetched_sr = frappe.get_doc("Service Request", sr.name)
        self.assertEqual(fetched_sr.custom_project, self.actual_test_sp_name)

    def test_validate_vyapolnena_requires_linked_report(self, frappe_site) -> None:
        """Test that a linked report is required to mark the request as completed."""
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)
        sr.status = STATUS_VYPOLNENA

        with self.assertRaisesRegex(frappe.ValidationError, "Нельзя отметить заявку выполненной без связанного отчёта"):
            sr.save()

    def test_hook_get_engineers_for_object(self, frappe_site) -> None:
        """Test the hook to get engineers for the service object."""
        from ferum_customs.custom_logic.service_request_hooks import get_engineers_for_object

        engineers = get_engineers_for_object(self.actual_test_so_name)
        self.assertIn(self.test_engineer_user_email, engineers)

    def test_sr_controller_internal_methods_with_custom_fields(self, frappe_site) -> None:
        """Test internal methods of Service Request controller with custom fields."""
        sr_doc = frappe.new_doc("Service Request")
        sr_doc.subject = " Test Subject for Cleaning "
        sr_doc.planned_start_datetime = now_datetime()
        sr_doc.planned_end_datetime = add_days(now_datetime(), -1)

        with self.assertRaisesRegex(frappe.ValidationError, "Планируемая дата начала не может быть позже"):
            sr_doc.validate()

        sr_doc.planned_end_datetime = add_days(now_datetime(), 1)
        sr_doc.actual_start_datetime = now_datetime()
        sr_doc.actual_end_datetime = add_days(sr_doc.actual_start_datetime, 0.5)

        sr_doc.validate()
        sr_doc.run_method("before_save")

        self.assertEqual(sr_doc.subject.strip(), "Test Subject for Cleaning")
        self.assertAlmostEqual(sr_doc.duration_hours, 12.0, places=2)

    @patch("frappe.sendmail")
    def test_notify_project_manager_on_close(self, mock_sendmail_func, frappe_site) -> None:
        """Test notification to project manager when the service request is closed."""
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)

        sr.reload()
        sr.status = STATUS_ZAKRYTA
        sr.save(ignore_permissions=True)

        mock_sendmail_func.assert_called_once()
        args, kwargs = mock_sendmail_func.call_args

        self.assertIn(self.test_pm_user_email, kwargs.get("recipients"))
        self.assertIn(sr.name, kwargs.get("subject"))
        self.assertEqual(kwargs.get("reference_doctype"), "Service Request")
        self.assertEqual(kwargs.get("reference_name"), sr.name)
        if sr.custom_customer:
            self.assertIn(self.test_customer_name, kwargs.get("message"))
