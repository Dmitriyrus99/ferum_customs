# ferum_customs/permissions/permissions.py
"""
Dynamic conditions for permission queries (Permission Query Conditions).

This module provides dynamic conditions for permission queries based on user roles and linked customers.
"""

from __future__ import annotations

from typing import Optional, Dict, List, Tuple
import frappe

from ferum_customs.constants import ROLE_CUSTOMER, ROLE_ZAKAZCHIK

PQCConditionValue = Union[str, List[Union[str, List[str]]], Dict[str, str], Tuple[str, str]]
PQCConditions = Dict[str, PQCConditionValue]


@frappe.whitelist()
def get_service_request_pqc(user: Optional[str] = None) -> Optional[PQCConditions]:
    """
    Get permission query conditions for service requests based on the user's roles and linked customer.

    Args:
        user (Optional[str]): The username of the user. If None, the current session user is used.

    Returns:
        Optional[PQCConditions]: A dictionary of conditions for permission queries or None if no conditions apply.
    """
    if user is None:
        user = frappe.session.user

    if user == "Administrator" or frappe.has_role("System Manager", user):
        return None

    try:
        user_doc = frappe.get_cached_doc("User", user)
    except frappe.DoesNotExistError:
        frappe.log(__name__).warning(
            f"User '{user}' not found while applying PQC for service_request."
        )
        return {"name": ("=", f"__no_records_user_not_found_{user}")}

    # Ensure the field 'customer' exists in the User DocType
    user_linked_customer = user_doc.get("customer")
    if user_linked_customer is None:
        frappe.log(__name__).warning(
            f"User '{user}' does not have a linked customer while applying PQC for service_request."
        )
        return {"name": ("=", f"__no_records_no_linked_customer_{user}")}

    is_customer_role = frappe.has_role(ROLE_ZAKAZCHIK, user) or frappe.has_role(
        ROLE_CUSTOMER, user
    )

    if is_customer_role:
        # A user with the role "Customer" and a linked customer can only see requests for their customer.
        return {"custom_customer": ("=", user_linked_customer)}

    return None
