# ferum_customs/ferum_customs/custom_logic/service_request_hooks.py
"""Хуки для DocType *Service Request*."""

from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.utils import get_link_to_form, now

from ..constants import (
    FIELD_CUSTOM_CUSTOMER,
    FIELD_CUSTOM_LINKED_REPORT,
    FIELD_CUSTOM_PROJECT,
    FIELD_CUSTOM_SERVICE_OBJECT_LINK,
    ROLE_PROEKTNYJ_MENEDZHER,
    STATUS_VYPOLNENA,
    STATUS_ZAKRYTA,
)

if TYPE_CHECKING:
    from frappe.model.document import Document as FrappeDocument

    from ..doctype.service_request.service_request import ServiceRequest


# --------------------------------------------------------------------------- #
#                               Doc Events                                  #
# --------------------------------------------------------------------------- #


def validate(doc: ServiceRequest, method: str | None = None) -> None:
    """
    Вызывается Frappe перед сохранением `Service Request`.
    Проверяем бизнес-правила.
    """
    if doc.status == STATUS_VYPOLNENA and not doc.get(FIELD_CUSTOM_LINKED_REPORT):
        frappe.throw(_("Нельзя отметить заявку выполненной без связанного отчёта."))

    if doc.status == STATUS_VYPOLNENA and not doc.get("completed_on"):
        doc.completed_on = now()

    if doc.get(FIELD_CUSTOM_PROJECT) and not doc.get(FIELD_CUSTOM_CUSTOMER):
        customer = frappe.db.get_value(
            "Service Project", doc.get(FIELD_CUSTOM_PROJECT), "customer"
        )
        if customer:
            doc.custom_customer = customer
        else:
            frappe.throw(
                _("У выбранного проекта ({0}) отсутствует связанный клиент.").format(
                    doc.get(FIELD_CUSTOM_PROJECT)
                )
            )

    if not doc.get(FIELD_CUSTOM_CUSTOMER) and doc.get(FIELD_CUSTOM_SERVICE_OBJECT_LINK):
        customer = frappe.db.get_value(
            "Service Object", doc.get(FIELD_CUSTOM_SERVICE_OBJECT_LINK), "customer"
        )
        if customer:
            doc.custom_customer = customer


def on_update_after_submit(doc: ServiceRequest, method: str | None = None) -> None:
    """Вызывается после обновления отправленного документа."""
    if doc.status == STATUS_ZAKRYTA:
        _notify_project_manager(doc)


def prevent_deletion_with_links(doc: ServiceRequest, method: str | None = None) -> None:
    """Запрещает удаление заявки, если на нее есть ссылки."""
    if linked_report := frappe.db.exists(
        "Service Report", {"service_request": doc.name}
    ):
        frappe.throw(
            _("Нельзя удалить заявку {0}, так как на нее ссылается отчет {1}.").format(
                doc.name, linked_report
            )
        )


# --------------------------------------------------------------------------- #
#                           Whitelisted Methods                             #
# --------------------------------------------------------------------------- #


@frappe.whitelist()
def get_engineers_for_object(service_object_name: str) -> list[str]:
    """Возвращает список инженеров, назначенных на объект обслуживания."""
    if not service_object_name:
        return []

    try:
        so_doc: FrappeDocument = frappe.get_doc("Service Object", service_object_name)
        engineers_table = so_doc.get("assigned_engineers") or []
        return list(
            {
                entry.get("engineer")
                for entry in engineers_table
                if entry.get("engineer")
            }
        )
    except frappe.DoesNotExistError:
        frappe.logger(__name__).info(
            f"Объект '{service_object_name}' не найден при поиске инженеров."
        )
        return []
    except Exception as e:
        frappe.logger(__name__).error(
            f"Ошибка при получении инженеров для объекта '{service_object_name}': {e}",
            exc_info=True,
        )
        return []


# --------------------------------------------------------------------------- #
#                               Вспомогательное                               #
# --------------------------------------------------------------------------- #


def _notify_project_manager(doc: ServiceRequest) -> None:
    """Отправляет уведомление о закрытии заявки менеджерам проекта."""
    try:
        recipients = frappe.get_all(
            "User",
            filters={"enabled": 1, "roles.role": ROLE_PROEKTNYJ_MENEDZHER},
            pluck="name",
            distinct=True,
        )

        customer_email = doc.get("customer_email")
        if customer_email:
            recipients.append(customer_email)
        else:
            frappe.logger(__name__).warning(
                f"Service Request '{doc.name}' has no customer_email field set"
            )

        if not recipients:
            frappe.logger(__name__).warning(
                _("Получатели с ролью '{0}' не найдены для уведомления.").format(
                    ROLE_PROEKTNYJ_MENEDZHER
                )
            )
            return

        subject = _("Заявка на обслуживание {0} закрыта").format(doc.name)
        customer_name = (
            frappe.get_cached_value("Customer", doc.custom_customer, "customer_name")
            if doc.custom_customer
            else ""
        )

        message = _(
            """
            <p>Заявка на обслуживание <b>{doc_name}</b> была переведена в статус «Закрыта».</p>
            <p>Тема: {subject}</p>
            <p>Клиент: {customer}</p>
            <p><a href="{link}">{link_text}</a></p>
            """
        ).format(
            doc_name=doc.name,
            subject=doc.subject,
            customer=customer_name or _("Не указан"),
            link=get_link_to_form("Service Request", doc.name),
            link_text=_("Просмотреть заявку"),
        )

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype="Service Request",
            reference_name=doc.name,
            now=True,
        )
    except Exception as e:
        frappe.logger(__name__).error(
            f"Не удалось отправить уведомление о закрытии заявки '{doc.name}': {e}",
            exc_info=True,
        )
