# ferum_customs/custom_logic/payroll_entry_hooks.py
"""Хуки для DocType *PayrollEntryCustom* (расширение штатного Payroll Entry)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _  # Для перевода строк

if TYPE_CHECKING:
	# Предполагаемая структура для импорта DocType:
	from ..doctype.payroll_entry_custom.payroll_entry_custom import PayrollEntryCustom

	# from ..doctype.service_report.service_report import ServiceReport # Если используется в расчетах


def validate(doc: PayrollEntryCustom, method: str | None = None) -> None:
	"""
	Проверяет корректность дат периода. Дата окончания не может быть раньше даты начала.

	Args:
	    doc: Экземпляр документа PayrollEntryCustom.
	    method: Имя вызвавшего метода (например, "on_submit", "validate").

	Raises:
	    frappe.ValidationError: Если дата окончания раньше даты начала.
	"""
	if doc.get("start_date") and doc.get("end_date"):
		if doc.end_date < doc.start_date:
			frappe.throw(
				_("Дата окончания периода расчета ({0}) не может быть раньше даты начала ({1}).").format(
					frappe.utils.formatdate(doc.end_date),
					frappe.utils.formatdate(doc.start_date),
				)
			)

	# Сюда можно добавить другие проверки для PayrollEntryCustom.
	# if not doc.get("employee"):
	#     frappe.throw(_("Не выбран сотрудник для расчета зарплаты."))


def before_save(doc: PayrollEntryCustom, method: str | None = None) -> None:
	"""Calculate ``total_payable`` before saving."""

	total_bonus = 0.0
	try:
		if doc.get("employee") and doc.get("start_date") and doc.get("end_date"):
			reports = frappe.get_all(
				"ServiceReport",
				filters={
					"custom_assigned_engineer": doc.employee,
					"posting_date": ["between", [doc.start_date, doc.end_date]],
					"docstatus": 1,
				},
				fields=["custom_bonus_amount"],
			)
			for r in reports:
				try:
					total_bonus += float(r.get("custom_bonus_amount") or 0)
				except (TypeError, ValueError):
					frappe.logger(__name__).warning(
						f"Invalid bonus value in ServiceReport '{r}' while calculating payroll"
					)

	except Exception as exc:
		frappe.logger(__name__).error(
			f"Error fetching ServiceReport bonuses for '{doc.name}': {exc}",
			exc_info=True,
		)

	base_salary = float(doc.get("base_salary", 0.0) or 0.0)
	additional_pay = float(doc.get("additional_pay", 0.0) or 0.0)
	total_deduction = float(doc.get("total_deduction", 0.0) or 0.0)

	doc.total_payable = base_salary + additional_pay + total_bonus - total_deduction

	if doc.get("total_payable") is None:
		doc.total_payable = 0.0

	if isinstance(doc.get("total_payable"), float | int):
		doc.total_payable = round(doc.total_payable, 2)
