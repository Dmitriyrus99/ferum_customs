# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CustomAttachment(Document):
	def on_trash(self):
		self.delete_file_from_google_drive()

	def delete_file_from_google_drive(self):
		# This requires the Google Drive integration to be configured
		# and the file to be uploaded to Google Drive.
		# The logic to delete the file from Google Drive would go here.
		pass