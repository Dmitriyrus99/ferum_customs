from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from ferum_customs.constants import STATUS_OTMENENA, STATUS_ZAKRYTA


def execute(
    filters: dict[str, Any] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    # Use parameterized queries to prevent SQL injection
    rows = frappe.db.sql(
        """
        SELECT custom_assigned_engineer AS engineer, COUNT(*) AS total
        FROM `tabservice_request`
        WHERE status NOT IN (%s, %s)
          AND custom_assigned_engineer IS NOT NULL
        GROUP BY custom_assigned_engineer
        ORDER BY total DESC
        """,
        (STATUS_ZAKRYTA, STATUS_OTMENENA),
        as_dict=True,
    )

    columns = [
        {
            "label": _("Engineer"),
            "fieldname": "engineer",
            "fieldtype": "Link",
            "options": "User",
            "width": 250,
        },
        {
            "label": _("Open Requests"),
            "fieldname": "total",
            "fieldtype": "Int",
            "width": 120,
        },
    ]

    return columns, rows
