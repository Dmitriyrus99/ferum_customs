from __future__ import annotations

import frappe
from frappe import _


def execute(filters=None):
	open_count = frappe.db.count(
		"service_request",
		{"status": ["not in", ("Закрыта", "Отменена")]},
	)
	overdue_count = frappe.db.count(
		"service_request",
		{
			"status": ["not in", ("Закрыта", "Отменена")],
			"planned_end_datetime": ("<", frappe.utils.now_datetime()),
		},
	)

	avg_seconds = (
		frappe.db.sql(
			"""
        select avg(timestampdiff(second, actual_start_datetime, actual_end_datetime))
        from `tabservice_request`
        where actual_end_datetime is not null
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
