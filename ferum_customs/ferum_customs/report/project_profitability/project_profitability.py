from __future__ import unicode_literals
import frappe

def execute(filters):
	columns, data = [], []
	columns = [
		{"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "ServiceProject", "width": 200},
		{"label": "Income", "fieldname": "income", "fieldtype": "Currency", "width": 150},
		{"label": "Expense", "fieldname": "expense", "fieldtype": "Currency", "width": 150},
		{"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 150}
	]

	# Logic to calculate project profitability
	data = []

	return columns, data
