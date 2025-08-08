# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PayrollEntryCustom(Document):
	def before_save(self):
		self.calculate_final_amount()

	def calculate_final_amount(self):
		self.final_amount = self.salary - self.advance_paid