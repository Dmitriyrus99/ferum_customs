from __future__ import annotations

from typing import Any, Optional

import frappe
from frappe import _

from ferum_customs.constants import STATUS_OTMENENA, STATUS_ZAKRYTA


def execute(
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Execute the service request overview report.

    Args:
        filters (Optional[Dict[str, Any]]): Filters to apply to the report.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: Columns and data for the report.
    """
    open_count = frappe.db.count(
        "service_request",
        {"status": ["not in", (STATUS_ZAKRYTA, STATUS_OTMENENA)]},
    )
    overdue_count = frappe.db.count(
        "service_request",
        {
            "status": ["not in", (STATUS_ZAKRYTA, STATUS_OTMENENA)],
            "planned_end_datetime": ("<", frappe.utils.now_datetime()),
        },
    )

    avg_seconds = (
        frappe.db.sql(
            """
            SELECT AVG(TIMESTAMPDIFF(SECOND, actual_start_datetime, actual_end_datetime))
            FROM `tabService Request`
            WHERE actual_end_datetime IS NOT NULL
            """,
            as_dict=False,
        )[0][0]
        or 0
    )
    avg_hours = round(avg_seconds / 3600.0, 2)

    columns = [
        {
            "label": _("Metric"),
            "fieldname": "metric",
            "fieldtype": "Data",
            "width": 250,
        },
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 120},
    ]

    data = [
        {"metric": _("Open Requests"), "value": open_count},
        {"metric": _("Overdue Requests"), "value": overdue_count},
        {"metric": _("Avg Resolution (h)"), "value": avg_hours},
    ]

    return columns, data
