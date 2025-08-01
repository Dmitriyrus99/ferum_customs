# ferum_customs/ferum_customs/custom_logic/service_object_hooks.py
"""Хуки для DocType *Service Object* – оборудование / объект обслуживания."""

from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _  # Для перевода строк

if TYPE_CHECKING:
    # Замените на актуальный путь к вашему DocType Service Object, если он определен.
    from ferum_customs.ferum_customs.doctype.service_object.service_object import (
        ServiceObject,
    )

def validate(doc: ServiceObject, method: str | None = None) -> None:
    """
    Проверяет уникальность серийного номера объекта обслуживания.
    Эта проверка является примером бизнес-требования.

    Args:
        doc: Экземпляр документа Service Object.
        method: Имя вызвавшего метода (например, "validate").

    Raises:
        frappe.ValidationError: Если серийный номер не уникален.
    """
    if doc.get("serial_no"):
        # Удаляем возможные пробелы по краям перед проверкой
        serial_no_cleaned = doc.serial_no.strip()
        if not serial_no_cleaned:  # Если после очистки строка пустая
            frappe.throw(_("Серийный номер не может состоять только из пробелов."))
            return

        # Формируем фильтры для поиска дубликатов.
        filters = {
            "serial_no": serial_no_cleaned,
            "name": ["!=", doc.name],
        }

        existing_doc_name = frappe.db.exists("Service Object", filters)

        if existing_doc_name:
            error_message = _(
                "Серийный номер '{0}' уже используется другим объектом обслуживания: {1}."
            ).format(serial_no_cleaned, existing_doc_name)
            frappe.throw(error_message, title=_("Ошибка уникальности"))

    # Сюда можно добавить другие проверки для ServiceObject.
    # Например, проверка связанных полей, форматов и т.д.
    # if doc.installation_date and doc.installation_date > frappe.utils.today():
    #     frappe.throw(_("Дата установки не может быть в будущем."))
