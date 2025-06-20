from unittest.mock import patch  # Для мокирования frappe.sendmail

import pytest

try:
    import frappe  # noqa: F401
    from frappe.tests.utils import FrappeTestCase
    from frappe.utils import add_days, now_datetime
except Exception:  # pragma: no cover
    pytest.skip("frappe not available", allow_module_level=True)

# Импортируйте ваши константы
from ferum_customs.constants import STATUS_OTKRYTA, STATUS_VYPOLNENA, STATUS_ZAKRYTA

# Constants used in tests. FrappeTestCase will provide matching fixtures.
TEST_CUSTOMER_NAME = "_Test Customer for SR Tests"
TEST_ENGINEER_USER_EMAIL = "test_sr_engineer_ferum@example.com"
TEST_PM_USER_EMAIL = "test_sr_pm_ferum@example.com"
TEST_SP_NAME_FIELD = "_Test SP for SR Tests"
ACTUAL_TEST_SP_NAME = TEST_SP_NAME_FIELD
ACTUAL_TEST_SO_NAME = "_Test SO for SR Tests"


class TestServiceRequest(FrappeTestCase):
    test_customer_name = TEST_CUSTOMER_NAME
    test_engineer_user_email = TEST_ENGINEER_USER_EMAIL
    test_pm_user_email = TEST_PM_USER_EMAIL
    test_sp_name_field = TEST_SP_NAME_FIELD
    actual_test_sp_name = ACTUAL_TEST_SP_NAME
    actual_test_so_name = ACTUAL_TEST_SO_NAME

    def setUp(self):
        frappe.db.savepoint()
        self.current_user_for_test = frappe.session.user
        frappe.set_user(self.test_pm_user_email)  # Действия от имени ПМ

    def tearDown(self):
        frappe.set_user(self.current_user_for_test)
        frappe.db.rollback()

    def create_service_request_doc(self, status=STATUS_OTKRYTA, submit_doc=False):
        sr = frappe.new_doc("Service Request")
        sr.subject = "Test SR - " + frappe.generate_hash(length=5)
        # Используем custom_ префиксы
        sr.custom_customer = self.test_customer_name
        sr.custom_service_object_link = self.actual_test_so_name
        # custom_project должен подтянуться из custom_service_object_link
        sr.request_datetime = now_datetime()
        sr.status = status
        sr.insert(ignore_permissions=True)  # insert вызовет before_save и validate
        if submit_doc and sr.docstatus == 0:
            try:
                sr.submit()
            except frappe.exceptions.DoesNotExistError as e:
                # Иногда workflow может быть не до конца синхронизирован в тестах
                if "WorkflowState" in str(e) and "Открыта" in str(
                    e
                ):  # Имя статуса из workflow_service_request.json
                    frappe.get_doc(
                        "Workflow State", {"workflow_state_name": "Открыта"}
                    ).save(ignore_permissions=True)
                    sr.reload()
                    sr.submit()
                else:
                    raise
        return sr

    def test_sr_creation_and_custom_fields(self, frappe_site):
        sr = self.create_service_request_doc()
        self.assertEqual(sr.custom_customer, self.test_customer_name)
        self.assertEqual(sr.custom_service_object_link, self.actual_test_so_name)

        # Проверяем, что custom_project подтянулся (логика в service_request.before_save)
        fetched_sr = frappe.get_doc("Service Request", sr.name)
        self.assertEqual(fetched_sr.custom_project, self.actual_test_sp_name)

    def test_validate_vyapolnena_requires_linked_report(self, frappe_site):
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)
        sr.status = STATUS_VYPOLNENA  # Имитируем изменение статуса
        # sr.custom_linked_report = None # Убедимся, что поле пустое (оно и так будет None для нового SR)

        with self.assertRaisesRegex(
            frappe.ValidationError,
            "Нельзя отметить заявку выполненной без связанного отчёта",
        ):
            sr.save()  # save вызовет validate

    def test_hook_get_engineers_for_object(self, frappe_site):
        from ferum_customs.custom_logic.service_request_hooks import (
            get_engineers_for_object,
        )

        engineers = get_engineers_for_object(self.actual_test_so_name)
        self.assertIn(self.test_engineer_user_email, engineers)

    def test_sr_controller_internal_methods_with_custom_fields(self, frappe_site):
        sr_doc = frappe.new_doc("Service Request")
        sr_doc.subject = " Test Subject for Cleaning "
        # Даты
        sr_doc.planned_start_datetime = now_datetime()
        sr_doc.planned_end_datetime = add_days(now_datetime(), -1)  # Некорректная дата

        with self.assertRaisesRegex(
            frappe.ValidationError, "Планируемая дата начала не может быть позже"
        ):
            sr_doc.validate()

        sr_doc.planned_end_datetime = add_days(now_datetime(), 1)
        sr_doc.actual_start_datetime = now_datetime()
        sr_doc.actual_end_datetime = add_days(
            sr_doc.actual_start_datetime, 0.5
        )  # 12 часов

        # Установка кастомных полей для проверки _clean_fields (если бы они очищались)
        # sr_doc.custom_customer = f" {self.test_customer_name} " # Пример для очистки, если бы она была для Link

        sr_doc.validate()
        sr_doc.run_method("before_save")

        self.assertEqual(sr_doc.subject, "Test Subject for Cleaning")
        # if sr_doc.custom_customer: # Если бы custom_customer очищался
        #     self.assertEqual(sr_doc.custom_customer, self.test_customer_name)
        self.assertAlmostEqual(sr_doc.duration_hours, 12.0, places=2)

    @patch("frappe.sendmail")  # Мокируем функцию frappe.sendmail
    def test_notify_project_manager_on_close(self, mock_sendmail_func, frappe_site):
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)

        # Имитируем изменение статуса на Закрыта
        # В реальной системе это произойдет через Workflow Action
        # Для теста хука on_update_after_submit, нужно чтобы документ был submitted (docstatus=1)
        # и чтобы изменилось отслеживаемое поле (например, status).
        sr.reload()  # Убедимся, что работаем с последней версией
        sr.status = STATUS_ZAKRYTA
        sr.save(
            ignore_permissions=True
        )  # Это вызовет on_update, который для submitted вызовет on_update_after_submit

        mock_sendmail_func.assert_called_once()
        args, kwargs = mock_sendmail_func.call_args

        self.assertIn(self.test_pm_user_email, kwargs.get("recipients"))
        self.assertIn(sr.name, kwargs.get("subject"))
        self.assertEqual(kwargs.get("reference_doctype"), "Service Request")
        self.assertEqual(kwargs.get("reference_name"), sr.name)
        # Проверка, что custom_customer используется в сообщении, если он есть
        if sr.custom_customer:
            self.assertIn(self.test_customer_name, kwargs.get("message"))
