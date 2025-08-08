# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Invoice(Document):
	def on_submit(self):
		self.add_to_google_sheet()

	def add_to_google_sheet(self):
		if self.party_type == "Supplier":
			# Logic to add a row to Google Sheet
			# This will require setting up Google API credentials
			pass

	@frappe.whitelist()
	def set_as_awaiting_payment(self):
		self.status = "Awaiting Payment"
		self.save()

	@frappe.whitelist()
	def set_as_paid(self):
		self.status = "Paid"
		self.save()
