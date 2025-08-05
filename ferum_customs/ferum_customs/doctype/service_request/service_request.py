# ferum_customs/ferum_customs/doctype/service_request/service_request.py
"""Python controller for DocType "Service Request"."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
    from frappe.types import DF

from frappe.utils import now_datetime

SLA_RULES = {
    "Maintenance": {"assign_within_min": 180, "close_within_hours": 72},
    "Emergency": {"assign_within_min": 15, "close_within_hours": 2},
}


class ServiceRequest(Document):
    """Business logic for service requests."""

    project: DF.Link | None
    object: DF.Link | None
    assign_by: DF.Datetime | None
    close_by: DF.Datetime | None

    def before_save(self) -> None:
        """Populate derived fields and apply SLA deadlines."""
        self.autofill_project_based_on_object()
        self.apply_sla_rules()

    def on_update(self) -> None:
        """Notify about status changes."""
        self.notify_status_change()

    def autofill_project_based_on_object(self) -> None:
        """Fill project based on the linked object when not set."""
        if self.object and not self.project:
            project = frappe.db.get_value("Service Object", self.object, "project")
            if project:
                self.project = project

    def notify_status_change(self) -> None:
        """Send a simple notification when status is updated."""
        previous = self.get_doc_before_save()
        if previous and previous.status != self.status:
            frappe.msgprint(
                _("Service Request {0} status changed from {1} to {2}.").format(
                    self.name, previous.status, self.status
                )
            )

    def apply_sla_rules(self) -> None:
        """Compute SLA deadlines based on request type."""
        rule = SLA_RULES.get(self.request_type)
        if not rule:
            return
        creation = self.creation or now_datetime()
        if not self.assign_by:
            self.assign_by = creation + timedelta(minutes=rule["assign_within_min"])
        if not self.close_by:
            self.close_by = creation + timedelta(hours=rule["close_within_hours"])
