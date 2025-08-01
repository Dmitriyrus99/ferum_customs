# ferum_customs/ferum_customs/doctype/service_object/service_object.py
"""
Python-контроллер для DocType "Service Object".
"""

from __future__ import annotations
from frappe.model.document import Document
import frappe
from frappe import _


class ServiceObject(Document):
    """
    Класс документа ServiceObject.
    """

    linked_service_project: str | None = None
    object_name: str | None = None
    warranty_expiry_date: str | None = None
    purchase_date: str | None = None

    def validate(self) -> None:
        """
        Валидация данных документа.
        Основная валидация уникальности серийного номера вынесена в
        `custom_logic.service_object_hooks.validate`.
        Здесь можно добавить специфичные для класса валидации.
        """
        self._clean_fields()

        # Пример дополнительной валидации:
        if self.warranty_expiry_date and self.purchase_date:
            if self.warranty_expiry_date < self.purchase_date:
                frappe.throw(_("Дата окончания гарантии не может быть раньше даты покупки."))

    def _clean_fields(self) -> None:
        """
        Очистка строковых полей.
        """
        if self.linked_service_project and isinstance(self.linked_service_project, str):
            self.linked_service_project = self.linked_service_project.strip()

        if self.object_name and isinstance(self.object_name, str):
            self.object_name = self.object_name.strip()
