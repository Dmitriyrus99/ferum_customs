from __future__ import unicode_literals
import frappe

def execute(filters):
	columns, data = [], []
	columns = [
		{"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
		{"label": "Total Salary", "fieldname": "total_salary", "fieldtype": "Currency", "width": 200}
	]

	# Logic to calculate monthly salary expense
	data = []

	return columns, data
