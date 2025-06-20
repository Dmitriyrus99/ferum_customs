# ferum_customs/ferum_customs/custom_logic/service_report_hooks.py
"""Хуки для DocType *ServiceReport*.

* Проверяем корректность привязки к заявке (validate).
* После отправки отчёта обновляем связанную `service_request`
  через `on_submit`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _

from ..constants import FIELD_CUSTOM_LINKED_REPORT, STATUS_VYPOLNENA

if TYPE_CHECKING:
	from ..doctype.service_report.service_report import ServiceReport
	from ..doctype.service_request.service_request import ServiceRequest


# --------------------------------------------------------------------------- #
#                           DocType events                                    #
# --------------------------------------------------------------------------- #



def validate(doc: ServiceReport, method: str | None = None) -> None:
	"""
	Проверяет, что отчёт ссылается на существующую заявку со статусом «Выполнена».
	Вызывается перед сохранением ServiceReport.

	Args:
	    doc: Экземпляр документа ServiceReport.
	    method: Имя вызвавшего метода (например, "validate").

	Raises:
	    frappe.ValidationError: Если нарушены бизнес-правила.
	"""
	if not doc.service_request:
		frappe.throw(_("Не выбрана связанная заявка на обслуживание (Service Request)."))

	if not frappe.db.exists("Service Request", doc.service_request):
		frappe.throw(
			_("Связанная заявка на обслуживание (Service Request) '{0}' не найдена.").format(
				doc.service_request
			)
		)

	req_status = frappe.db.get_value("Service Request", doc.service_request, "status")

	if not req_status:
		frappe.logger(__name__).error(
			_("Не удалось получить статус для заявки '{0}', связанной с отчетом '{1}'.").format(
				doc.service_request, doc.name
			)
		)
		frappe.throw(
			_("Не удалось получить статус для связанной заявки '{0}'. Обратитесь к администратору.").format(
				doc.service_request
			)
		)

	if req_status != STATUS_VYPOLNENA:
		frappe.throw(
			_("Отчёт можно привязать только к заявке в статусе «{0}». Текущий статус заявки «{1}».").format(
				STATUS_VYPOLNENA, req_status
			)
		)



def on_submit(doc: ServiceReport, method: str | None = None) -> None:

	"""
	После отправки (submit) отчёта обновляет связанную service_request.

	Действия:
	1. Записывает ссылку на этот отчёт в поле `custom_linked_report` связанной service_request.
	2. Убеждается, что статус связанной заявки установлен в «Выполнена».

	Args:
	    doc: Экземпляр документа ServiceReport.
	    method: Имя вызвавшего метода (например, "on_submit").
	"""
	if not doc.service_request:
		frappe.logger(__name__).warning(
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
		frappe.logger(__name__).info(f"Заявка '{req.name}' обновлена из отчета '{doc.name}'.")

	except frappe.DoesNotExistError:
		frappe.logger(__name__).error(
			_("Заявка '{0}', указанная в отчете '{1}', не найдена.").format(doc.service_request, doc.name),
			exc_info=True,
		)
	except Exception as e:
		frappe.logger(__name__).error(
			_("Ошибка при обновлении заявки '{0}' из отчета '{1}': {2}").format(
				doc.service_request, doc.name, e
			),
			exc_info=True,
		)
		frappe.throw(_("Произошла ошибка при обновлении связанной заявки. Обратитесь к администратору."))
