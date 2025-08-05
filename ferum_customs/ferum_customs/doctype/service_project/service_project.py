# ferum_customs/ferum_customs/doctype/service_project/service_project.py
"""Python controller for DocType "Service Project"."""

from __future__ import annotations

from typing import cast

import frappe
from frappe import _
from frappe.model.document import Document


class ServiceProject(Document):
    """Business logic for service projects."""

    def validate(self) -> None:
        """Validate project fields before saving."""
        self.check_dates_and_amount()
        self._validate_unique_objects()

    def check_dates_and_amount(self) -> None:
        """Ensure dates are ordered correctly and amount is non-negative."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("End date cannot be before start date."))

        if self.total_amount is not None:
            try:
                if float(self.total_amount) < 0:
                    frappe.throw(_("Total amount cannot be negative."))
            except (TypeError, ValueError):
                frappe.throw(_("Total amount must be a number."))

    def _validate_unique_objects(self) -> None:
        """Ensure each service object is unique and not linked to other projects."""
        rows: list[dict] = self.get("objects") or []
        seen: set[str] = set()
        for idx, row in enumerate(rows, start=1):
            obj = row.get("service_object")
            if not obj:
                frappe.throw(_("Service Object is required (row {0}).").format(idx))

            obj = cast(str, obj)
            if obj in seen:
                frappe.throw(
                    _("Service Object {0} is duplicated in this project.").format(obj)
                )
            seen.add(obj)

            existing_parent = frappe.db.get_value(
                "Project Object Item",
                {"service_object": obj, "parent": ["!=", self.name]},
                "parent",
            )
            if existing_parent:
                frappe.throw(
                    _("Service Object {0} is already linked to project {1}.").format(
                        obj, existing_parent
                    )
                )
