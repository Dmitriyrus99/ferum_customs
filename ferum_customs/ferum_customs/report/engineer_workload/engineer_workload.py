from __future__ import annotations

import frappe
from frappe import _


def execute(filters=None):
	rows = frappe.db.sql(
		"""
        select custom_assigned_engineer as engineer, count(*) as total
        from `tabservice_request`
        where status not in ('Закрыта', 'Отменена')
          and custom_assigned_engineer is not null
        group by custom_assigned_engineer
        order by total desc
        """,
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
