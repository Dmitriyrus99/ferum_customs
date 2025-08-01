# ferum_customs/ferum_customs/doctype/custom_attachment/custom_attachment.py
"""
Python-контроллер для DocType "Custom Attachment".
"""

from __future__ import annotations
from typing import Optional

import frappe
from frappe import _  # Для возможных пользовательских сообщений
from frappe.model.document import Document

class CustomAttachment(Document):
    """
    Класс документа CustomAttachment.
    
    Attributes:
        attachment_type (Optional[str]): Тип вложения.
    """
    attachment_type: Optional[str] = None

    def validate(self) -> None:
        """
        Валидация данных документа.
        Очищает и приводит к нижнему регистру `attachment_type`.
        Очищает `attachment_file`.
        """
        self._clean_fields()
        self._validate_parent_references()

    def _clean_fields(self) -> None:
        """
        Очистка строковых полей.
        """
        if self.attachment_type and isinstance(self.attachment_type, str):
            self.attachment_type = self.attachment_type.strip().lower()

    def _validate_parent_references(self) -> None:
        """
        Проверяет, что указана хотя бы одна родительская ссылка (на service_request, ServiceReport и т.д.),
        и что эти ссылки указывают на существующие документы.
        """
        parent_fields_map = {
            "parent_reference_sr": "Service Request",
            "parent_reference_srep": "Service Report",
            "parent_reference_so": "Service Object",
        }

        linked_parents_count = 0
        for field_name, doctype_name in parent_fields_map.items():
            parent_doc_id = self.get(field_name)
            if parent_doc_id:
                linked_parents_count += 1
                if not frappe.db.exists(doctype_name, parent_doc_id):
                    frappe.throw(
                        _("Связанный документ {0} с ID '{1}' не найден.").format(
                            frappe.get_doc_label(doctype_name) or doctype_name,
                            parent_doc_id,
                        ),
                        title=_("Ошибка связи"),
                    )

        # Пример бизнес-правила: должен быть указан хотя бы один родитель
        if linked_parents_count == 0 and not self.is_new():
            frappe.throw(_("Необходимо указать ссылку хотя бы на один родительский документ (Заявка, Отчет или Объект)."))

        # Пример бизнес-правила: должен быть указан ТОЛЬКО один родитель
        if linked_parents_count > 1:
            frappe.throw(_("Можно указать ссылку только на один родительский документ."))

    # Хук on_trash для CustomAttachment теперь обрабатывается в
    # ferum_customs.custom_logic.file_attachment_utils.on_custom_attachment_trash
    # и вызывается через hooks.py.
    # def on_trash(self) -> None:
    #     # Логика удаления физического файла и связанной File DocType записи.
    #     pass
