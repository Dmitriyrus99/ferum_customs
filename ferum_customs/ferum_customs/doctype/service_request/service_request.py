# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ServiceRequest(Document):
	def validate(self):
		self.prevent_closing_without_report()

	def prevent_closing_without_report(self):
		if self.status == "Closed":
			has_report = frappe.db.exists("ServiceReport", {"service_request": self.name})
			if not has_report:
				frappe.throw("Cannot close a Service Request without a Service Report.")