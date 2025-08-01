from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import frappe
    from frappe import _
except ImportError:
    raise ImportError("Frappe module is not installed.")

from ferum_customs.constants import FIELD_CUSTOM_LINKED_REPORT, STATUS_VYPOLNENA

if TYPE_CHECKING:
    from ferum_customs.ferum_customs.doctype.service_report.service_report import (
        ServiceReport,
    )
    from ferum_customs.ferum_customs.doctype.service_request.service_request import (
        ServiceRequest,
    )

def validate(doc: ServiceReport, method: str | None = None) -> None:
    if not doc.service_request:
        raise frappe.ValidationError(
            _("Не выбрана связанная заявка на обслуживание (Service Request).")
        )

    if not frappe.db.exists("Service Request", doc.service_request):
        raise frappe.ValidationError(
            _(
                "Связанная заявка на обслуживание (Service Request) '{0}' не найдена."
            ).format(doc.service_request)
        )

    req_status = frappe.db.get_value("Service Request", doc.service_request, "status")

    if req_status is None:
        frappe.logger().error(
            _(
                "Не удалось получить статус для заявки '{0}', связанной с отчетом '{1}'."
            ).format(doc.service_request, doc.name)
        )
        raise frappe.ValidationError(
            _(
                "Не удалось получить статус для связанной заявки '{0}'. Обратитесь к администратору."
            ).format(doc.service_request)
        )

    if req_status != STATUS_VYPOLNENA:
        raise frappe.ValidationError(
            _(
                "Отчёт можно привязать только к заявке в статусе «{0}». Текущий статус заявки «{1}»."
            ).format(STATUS_VYPOLNENA, req_status)
        )

def on_submit(doc: ServiceReport, method: str | None = None) -> None:
    if not doc.service_request:
        frappe.logger().warning(
            f"Отчет '{doc.name}' отправлен без ссылки на заявку. Пропущено обновление."
        )
        return

    try:
        req: ServiceRequest = frappe.get_doc("Service Request", doc.service_request)

        req.set(FIELD_CUSTOM_LINKED_REPORT, doc.name)

        if req.status != STATUS_VYPOLNENA:
            req.status = STATUS_VYPOLNENA
            if req.meta.has_field("completed_on") and not req.get("completed_on"):
                req.completed_on = frappe.utils.now()

        req.save(ignore_permissions=True)

        frappe.msgprint(
            _("Связанная заявка на обслуживание {0} была обновлена.").format(req.name),
            indicator="green",
            alert=True,
        )
        frappe.logger().info(
            f"Заявка '{req.name}' обновлена из отчета '{doc.name}'."
        )

    except frappe.DoesNotExistError:
        frappe.logger().error(
            _("Заявка '{0}', указанная в отчете '{1}', не найдена.").format(
                doc.service_request, doc.name
            ),
            exc_info=True,
        )
    except Exception as e:
        frappe.logger().error(
            _("Ошибка при обновлении заявки '{0}' из отчета '{1}': {2}").format(
                doc.service_request, doc.name, e
            ),
            exc_info=True,
        )
        raise frappe.ValidationError(
            _(
                "Произошла ошибка при обновлении связанной заявки. Обратитесь к администратору."
            )
        )
