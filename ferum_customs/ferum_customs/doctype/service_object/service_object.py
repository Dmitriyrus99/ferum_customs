# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ServiceObject(Document):
	def on_trash(self):
		self.prevent_deletion_if_active_requests()

	def prevent_deletion_if_active_requests(self):
		active_requests = frappe.get_all(
			"ServiceRequest",
			filters={
				"service_object": self.name,
				"status": ["!=", "Closed"]
			}
		)
		if active_requests:
			frappe.throw(f"Cannot delete Service Object {self.name} as there are active service requests associated with it.")