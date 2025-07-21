# ferum_customs/ferum_customs/doctype/service_object/service_object.py
"""
Python-контроллер для DocType "Service Object".
"""

from __future__ import annotations

# from typing import TYPE_CHECKING
# from frappe import _ # Если будут пользовательские сообщения
# if TYPE_CHECKING:
# from ..service_project.service_project import ServiceProject # Пример
# from .assigned_engineer_item import AssignedEngineerItem # Для дочерней таблицы
# pass
from typing import Optional

from frappe.model.document import Document


class ServiceObject(Document):  # type: ignore[misc]
    """
    Класс документа ServiceObject.
    """

    linked_service_project: str | None

    def validate(self) -> None:
        """
        Валидация данных документа.
        Основная валидация уникальности серийного номера вынесена в
        `custom_logic.service_object_hooks.validate`.
        Здесь можно добавить специфичные для класса валидации.
        """
        self._clean_fields()

        # Пример дополнительной валидации:
        # if self.get("warranty_expiry_date") and self.get("purchase_date"):
        #     if self.warranty_expiry_date < self.purchase_date:
        #         frappe.throw(_("Дата окончания гарантии не может быть раньше даты покупки."))

        # Логика из оригинального файла (service_object.py):
        # if self.linked_service_project:
        #     self.linked_service_project = self.linked_service_project.strip()
        # Эта логика теперь в _clean_fields()

    def _clean_fields(self) -> None:
        """
        Очистка строковых полей.
        """
        # Поля типа Link обычно не требуют strip(), так как хранят ID.
        # Если 'linked_service_project' - это Data поле, то strip() имеет смысл.
        # Предположим, что это Link, поэтому strip() здесь может быть излишним,
        # но оставлен для соответствия оригинальному коду, если там была причина.
        if self.get("linked_service_project") and isinstance(
            self.linked_service_project, str
        ):
            self.linked_service_project = self.linked_service_project.strip()

        # if self.get("object_name"):
        #     self.object_name = self.object_name.strip()
        pass

    # Другие методы жизненного цикла (before_save, on_submit, etc.) могут быть добавлены по необходимости.
