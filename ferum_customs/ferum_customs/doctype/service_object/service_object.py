# ferum_customs/ferum_customs/doctype/service_object/service_object.py
"""Python controller for DocType "Service Object"."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ServiceObject(Document):
    """Business logic for service objects."""

    def validate(self) -> None:
        """Ensure uniqueness of object within the project."""
        self._ensure_unique_per_project()

    def on_trash(self) -> None:
        """Prevent deletion if there are active service requests."""
        self.block_delete_if_active_requests()

    def _ensure_unique_per_project(self) -> None:
        if not (self.object_name and self.project):
            return
        exists = frappe.db.exists(
            "Service Object",
            {
                "object_name": self.object_name,
                "project": self.project,
                "name": ["!=", self.name],
            },
        )
        if exists:
            frappe.throw(
                _("Object {0} already exists for this project.").format(
                    self.object_name
                )
            )

    def block_delete_if_active_requests(self) -> None:
        """Disallow deletion when active Service Requests are linked."""
        has_open = frappe.db.exists(
            "Service Request",
            {"object": self.name, "status": ["not in", ["Closed", "Закрыта"]]},
        )
        if has_open:
            frappe.throw(_("Cannot delete object linked to active service requests."))
