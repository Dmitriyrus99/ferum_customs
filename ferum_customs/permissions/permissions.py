# ferum_customs/permissions/permissions.py
"""
Динамические условия для запросов разрешений (Permission Query Conditions).
"""

from __future__ import annotations

import frappe

from ferum_customs.constants import ROLE_CUSTOMER, ROLE_ZAKAZCHIK

PQCConditionValue = str | list[str | list[str]] | dict[str, str] | tuple[str, str]
PQCConditions = dict[str, PQCConditionValue]


def get_service_request_pqc(user: str | None = None) -> PQCConditions | None:
    if user is None:
        user = frappe.session.user

    if user == "Administrator" or frappe.has_role("System Manager", user):
        return None

    try:
        user_doc = frappe.get_cached_doc("User", user)
    except frappe.DoesNotExistError:
        frappe.logger(__name__).warning(
            f"User '{user}' not found while applying PQC for service_request."
        )
        return {"name": ("=", f"__no_records_user_not_found_{user}")}

    # Ensure the field 'customer' exists in the User DocType
    user_linked_customer = user_doc.get("customer")
    if user_linked_customer is None:
        frappe.logger(__name__).warning(
            f"User '{user}' does not have a linked customer while applying PQC for service_request."
        )
        return {"name": ("=", f"__no_records_no_linked_customer_{user}")}

    is_customer_role = frappe.has_role(ROLE_ZAKAZCHIK, user) or frappe.has_role(
        ROLE_CUSTOMER, user
    )

    if is_customer_role:
        # Пользователь с ролью "Заказчик" и привязанным клиентом видит только заявки своего клиента.
        return {"custom_customer": user_linked_customer}

    return None
