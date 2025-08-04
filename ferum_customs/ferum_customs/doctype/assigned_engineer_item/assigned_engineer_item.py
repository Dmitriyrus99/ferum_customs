# ferum_customs/ferum_customs/doctype/assigned_engineer_item/assigned_engineer_item.py
"""
Python controller for the child DocType "Assigned Engineer Item".
This DocType is used as a table in another document (e.g., Service Object).
"""

from __future__ import annotations

import datetime
from typing import Optional

import frappe
from frappe.model.document import Document


class AssignedEngineerItem(Document):
    """
    Document class for the AssignedEngineerItem child table.
    """

    engineer: str | None = None
    assignment_date: str | None = None

    def validate(self) -> None:
        """
        Validate data for the child table row.
        """
        super().validate()  # Ensure parent validation is called
        self._clean_engineer_field()
        self._format_assignment_date()

    def _clean_engineer_field(self) -> None:
        """
        Cleans the engineer field.
        """
        if self.engineer and isinstance(self.engineer, str):
            original_value = self.engineer
            self.engineer = self.engineer.strip()
            if self.engineer != original_value:
                frappe.log(__name__).debug(
                    f"Stripped whitespace from 'engineer' field in AssignedEngineerItem (parent: {self.parent}), original: '{original_value}', new: '{self.engineer}'"
                )

    def _format_assignment_date(self) -> None:
        """
        Formats the assignment date to ISO format.
        """
        assignment_date_val = self.get("assignment_date")
        if assignment_date_val:
            if isinstance(assignment_date_val, datetime.datetime | datetime.date):
                self.assignment_date = assignment_date_val.isoformat()
            elif isinstance(assignment_date_val, str):
                try:
                    dt_obj = frappe.utils.get_datetime(assignment_date_val)
                    self.assignment_date = dt_obj.isoformat()
                except (ValueError, TypeError):
                    frappe.log(__name__).warning(
                        f"Could not parse or re-format 'assignment_date' string '{assignment_date_val}' in AssignedEngineerItem (parent: {self.parent})."
                    )
