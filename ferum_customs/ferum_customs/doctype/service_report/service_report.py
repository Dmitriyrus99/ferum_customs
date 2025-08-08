# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ServiceReport(Document):
	def on_submit(self):
		self.update_service_request_status()

	def update_service_request_status(self):
		frappe.db.set_value("ServiceRequest", self.service_request, "status", "Closed")