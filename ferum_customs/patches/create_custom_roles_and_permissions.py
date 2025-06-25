"""Create essential roles and permissions during installation."""

from __future__ import annotations

import frappe

ROLES = [
    "Проектный менеджер",
    "Инженер",
    "Заказчик",
]

SERVICE_REQUEST_PERMS = [
    {
        "parent": "Service Request",
        "role": "Проектный менеджер",
        "permlevel": 0,
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "submit": 1,
        "cancel": 1,
        "amend": 1,
        "report": 1,
        "share": 1,
        "print": 1,
        "email": 1,
        "if_owner": 0,
    },
    {
        "parent": "Service Request",
        "role": "Инженер",
        "permlevel": 0,
        "read": 1,
        "write": 1,
        "create": 0,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0,
        "report": 1,
        "share": 1,
        "print": 1,
        "email": 1,
        "if_owner": 0,
    },
    {
        "parent": "Service Request",
        "role": "Заказчик",
        "permlevel": 0,
        "read": 1,
        "write": 0,
        "create": 1,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0,
        "report": 0,
        "share": 0,
        "print": 1,
        "email": 1,
        "if_owner": 1,
    },
]


def create_role(role_name: str) -> None:
    """Ensure that a Role with the given name exists."""

    if frappe.db.exists("Role", role_name):
        return

    role = frappe.get_doc({"doctype": "Role", "role_name": role_name})
    role.insert(ignore_permissions=True)


def create_docperm(perm: dict[str, int | str]) -> None:
    """Insert DocPerm if it is missing."""

    filters = {
        "parent": perm["parent"],
        "role": perm["role"],
        "permlevel": perm.get("permlevel", 0),
    }

    if frappe.db.exists("DocPerm", filters):
        return

    perm_doc = frappe.get_doc({
        **perm,
        "doctype": "DocPerm",
        "parenttype": "DocType",
        "parentfield": "permissions",
    })
    perm_doc.insert(ignore_permissions=True)


def execute() -> None:
    """Create default roles and permissions for the app."""

    for role in ROLES:
        create_role(role)

    for perm in SERVICE_REQUEST_PERMS:
        create_docperm(perm)

