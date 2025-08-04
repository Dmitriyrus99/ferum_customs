# ferum_customs/ferum_customs/custom_logic/service_object_hooks.py
"""Hooks for DocType *Service Object* – equipment / service object."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import frappe
from frappe import _  # For translation

if TYPE_CHECKING:
    from ferum_customs.ferum_customs.doctype.service_object.service_object import (
        ServiceObject,
    )


def validate(doc: ServiceObject) -> None:
    """
    Checks the uniqueness of the service object's serial number.
    This check is an example of a business requirement.

    Args:
        doc: An instance of the Service Object document.

    Raises:
        frappe.ValidationError: If the serial number is not unique or empty.
    """
    if doc.get("serial_no"):
        serial_no_cleaned = doc.serial_no.strip()
        if not serial_no_cleaned:
            frappe.throw(
                _("Serial number cannot be empty."), title=_("Validation Error")
            )

        filters = {
            "serial_no": serial_no_cleaned,
            "name": ["!=", doc.name],
        }

        existing_doc_name = frappe.db.exists("Service Object", filters)

        if existing_doc_name:
            error_message = _(
                "Serial number '{0}' is already used by another service object: {1}."
            ).format(serial_no_cleaned, existing_doc_name)
            frappe.throw(error_message, title=_("Uniqueness Error"))

    # Additional checks for ServiceObject can be added here.
