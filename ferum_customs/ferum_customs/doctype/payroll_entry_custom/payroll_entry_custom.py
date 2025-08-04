# ferum_customs/ferum_customs/doctype/payroll_entry_custom/payroll_entry_custom.py
"""
Python-контроллер для DocType "Payroll Entry Custom".
"""

from __future__ import annotations

from typing import Optional

import frappe
from frappe.model.document import Document


class PayrollEntryCustom(Document):
    total_payable: float | None = None
    total_deductions: float | None = None
    net_payable: float | None = None
    """
    Класс документа PayrollEntryCustom.
    """

    def validate(self) -> None:
        """
        Валидация данных документа.
        Проверка дат (start_date, end_date) вынесена в
        `custom_logic.payroll_entry_hooks.validate`.
        Расчет `total_payable` вынесен в
        `custom_logic.payroll_entry_hooks.before_save`.
        Здесь можно добавить специфичные для класса валидации.
        """
        self._round_total_payable()
        self._round_total_deductions()
        self._calculate_net_payable()

    def _round_total_payable(self) -> None:
        """
        Округляет поле `total_payable` до двух знаков после запятой, если оно установлено и является числом.
        """
        if self.get("total_payable") is not None:
            try:
                payable_float = float(self.get("total_payable") or 0.0)
                self.total_payable = round(payable_float, 2)
            except (ValueError, TypeError):
                pass  # Log error if necessary

    def _round_total_deductions(self) -> None:
        if self.get("total_deductions") is not None:
            try:
                deductions_float = float(self.get("total_deductions") or 0.0)
                self.total_deductions = round(deductions_float, 2)
            except (ValueError, TypeError):
                pass

    def _calculate_net_payable(self) -> None:
        try:
            pay = float(self.get("total_payable") or 0.0)
            ded = float(self.get("total_deductions") or 0.0)
            self.net_payable = round(pay - ded, 2)
        except (ValueError, TypeError):
            self.net_payable = None

    def before_save(self) -> None:
        """Расчитывает ``total_payable`` с учетом бонусов из Service Report."""
        total_bonus = 0.0
        try:
            if self.get("employee") and self.get("start_date") and self.get("end_date"):
                reports = frappe.get_all(
                    "ServiceReport",
                    filters={
                        "custom_assigned_engineer": self.get("employee"),
                        "posting_date": [
                            "between",
                            [self.get("start_date"), self.get("end_date")],
                        ],
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
                f"Error fetching ServiceReport bonuses for '{self.name}': {exc}",
                exc_info=True,
            )

        base_salary = float(self.get("base_salary", 0.0) or 0.0)
        additional_pay = float(self.get("additional_pay", 0.0) or 0.0)
        total_deduction = float(self.get("total_deduction", 0.0) or 0.0)

        self.total_payable = (
            base_salary + additional_pay + total_bonus - total_deduction
        )

        if self.total_payable is None:
            self.total_payable = 0.0

        if isinstance(self.total_payable, float | int):
            self.total_payable = round(self.total_payable, 2)
