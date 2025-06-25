# ferum_customs/install.py
"""
Код, выполняемый после установки приложения `ferum_customs`.

Может использоваться для создания начальных данных, ролей,
пользовательских полей (хотя фикстуры предпочтительнее для этого),
или других настроек, необходимых для работы приложения.
"""

import frappe
from frappe import _  # Для возможных сообщений

# Импорт констант ролей, если они используются
# from .constants import (
#     ROLE_PROEKTNYJ_MENEDZHER,
#     ROLE_OFIS_MENEDZHER,
#     ROLE_INZHENER,
#     ROLE_ZAKAZCHIK
# )


def after_install() -> None:
    """
    Вызывается один раз после успешной установки приложения.
    """
    frappe.db.commit()  # Коммит предыдущих транзакций перед началом операций в after_install, если необходимо
    # Создание ролей выполняется через фикстуры (fixtures/role.json).
    # Дополнительная логика установки может быть добавлена при необходимости.

    # Пример: Добавление пользовательских полей программно (обычно делается через fixtures/custom_field.json)
    # add_custom_fields()

    # Пример: Установка прав доступа по умолчанию (обычно делается через fixtures/custom_docperm.json)
    # setup_default_permissions()

    # Пример: Создание начальных данных
    # create_initial_data()

    frappe.db.commit()  # Финальный коммит
    frappe.msgprint(
        _(
            "Ferum Customs application installed successfully. Please check system settings and user roles."
        ),
        title=_("Installation Complete"),
        indicator="green",
    )


# Пример функции для добавления Custom Fields (не рекомендуется, лучше фикстуры)
# def add_custom_fields():
#     if not frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "custom_user_department"}):
#         frappe.get_doc({
#             "doctype": "Custom Field",
#             "dt": "User",
#             "fieldname": "custom_user_department",
#             "label": "Department (Custom)",
#             "fieldtype": "Link",
#             "options": "Department",
#             "insert_after": "role_profile_name" # Пример
#         }).insert()

# Пример функции для создания начальных данных
# def create_initial_data():
#     if not frappe.db.exists("ServiceType", {"service_type_name": "Standard Maintenance"}): # Пример DocType
#         frappe.get_doc({
#             "doctype": "ServiceType",
#             "service_type_name": "Standard Maintenance",
#             "default_duration_hours": 2
#         }).insert()
