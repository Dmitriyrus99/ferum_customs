# ferum_customs/ferum_customs/doctype/payroll_entry_custom/payroll_entry_custom.py
"""
Python-контроллер для DocType "Payroll Entry Custom".
"""

from __future__ import annotations

# import frappe # Не используется напрямую в этом файле, кроме как для frappe.model.document.Document
from typing import Optional

from frappe.model.document import Document

# from typing import TYPE_CHECKING


# from frappe import _ # Если будут пользовательские сообщения

# if TYPE_CHECKING:
# pass


class PayrollEntryCustom(Document):
    total_payable: float | None
    total_deductions: float | None
    net_payable: float | None
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

        # Логика из оригинального файла (payroll_entry_custom.py):
        # if self.total_payable is not None:
        #     self.total_payable = round(float(self.total_payable), 2)
        # Эта логика теперь в _round_total_payable()

    def _round_total_payable(self) -> None:
        """
        Округляет поле `total_payable` до двух знаков после запятой, если оно установлено и является числом.
        """
        if self.get("total_payable") is not None:
            try:
                # Преобразуем в float перед округлением, на случай если это строка или Decimal
                payable_float = float(self.total_payable or 0.0)
                self.total_payable = round(payable_float, 2)
            except (ValueError, TypeError):
                # Если значение не может быть преобразовано в float, логируем или выбрасываем ошибку.
                # В данном случае, просто не изменяем значение, если оно не числовое.
                # Это может быть обработано другими валидациями (например, тип поля Currency).
                pass  # Или frappe.log_error(...)

    def _round_total_deductions(self) -> None:
        if self.get("total_deductions") is not None:
            try:
                deductions_float = float(self.total_deductions or 0.0)
                self.total_deductions = round(deductions_float, 2)
            except (ValueError, TypeError):
                pass

    def _calculate_net_payable(self) -> None:
        try:
            pay = float(self.total_payable or 0.0)
            ded = float(self.total_deductions or 0.0)
            self.net_payable = round(pay - ded, 2)
        except (ValueError, TypeError):
            # Если не удалось привести к числам, не задаем значение
            self.net_payable = None

    # Другие методы жизненного цикла (before_save, on_submit, etc.) могут быть добавлены по необходимости.
    # before_save: Логика расчета total_payable находится в custom_logic.payroll_entry_hooks.before_save
