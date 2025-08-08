# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ServiceProject(Document):
	def validate(self):
		self.validate_duplicate_service_objects()

	def validate_duplicate_service_objects(self):
		seen_objects = []
		for item in self.get("service_objects"):
			if item.service_object in seen_objects:
				frappe.throw(f"Service Object {item.service_object} is duplicated in the project.")
			seen_objects.append(item.service_object)