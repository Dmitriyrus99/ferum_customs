# ferum_customs/ferum_customs/doctype/assigned_engineer_item/assigned_engineer_item.py
"""
Python-контроллер для дочернего DocType "Assigned Engineer Item".
Этот DocType используется как таблица в другом документе (например, Service Object).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

import frappe
from frappe.model.document import Document

if TYPE_CHECKING:
    pass


class AssignedEngineerItem(Document):
    """
    Класс документа (дочерней таблицы) AssignedEngineerItem.
    """

    engineer: Optional[str]
    assignment_date: Optional[str]

    def validate(self) -> None:
        """
        Валидация данных для строки дочерней таблицы.
        """
        self._clean_engineer_field()
        self._format_assignment_date()

    def _clean_engineer_field(self) -> None:
        """
        Очищает поле инженера.
        """
        if self.engineer and isinstance(self.engineer, str):
            original_value = self.engineer
            self.engineer = self.engineer.strip()
            if self.engineer != original_value:
                frappe.logger(__name__).debug(
                    f"Stripped whitespace from 'engineer' field in AssignedEngineerItem (parent: {self.parent}), original: '{original_value}', new: '{self.engineer}'"
                )

    def _format_assignment_date(self) -> None:
        """
        Форматирует дату назначения в ISO формат.
        """
        assignment_date_val = self.get("assignment_date")
        if assignment_date_val:
            if isinstance(assignment_date_val, (datetime.datetime, datetime.date)):
                self.assignment_date = assignment_date_val.isoformat()
            elif isinstance(assignment_date_val, str):
                try:
                    dt_obj = frappe.utils.get_datetime(assignment_date_val)
                    self.assignment_date = dt_obj.isoformat()
                except (ValueError, TypeError):
                    frappe.logger(__name__).warning(
                        f"Could not parse or re-format 'assignment_date' string '{assignment_date_val}' in AssignedEngineerItem (parent: {self.parent})."
                    )
