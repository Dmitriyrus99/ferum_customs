from __future__ import annotations

from typing import Any, Optional, Tuple, List, Dict

import frappe
from frappe import _

from ferum_customs.constants import STATUS_OTMENENA, STATUS_ZAKRYTA


@frappe.whitelist()
def execute(
    filters: Optional[dict] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Execute the engineer workload report.

    Args:
        filters (Optional[dict]): Optional filters for the report.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: A tuple containing the columns and rows of the report.
    """
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
