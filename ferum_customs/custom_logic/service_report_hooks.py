"""Hooks for Service Report DocType."""

from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _

from ferum_customs.constants import STATUS_CLOSED

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from ferum_customs.ferum_customs.doctype.service_report.service_report import (
        ServiceReport,
    )


def validate(doc: ServiceReport, method: str | None = None) -> None:
    """Ensure the Service Report has a linked Service Request."""

    if not doc.service_request:
        frappe.throw(
            _("Не выбрана связанная заявка на обслуживание (Service Request).")
        )


def calculate_total_payable(doc: ServiceReport, method: str | None = None) -> None:
    """Recalculate totals before saving the document."""

    doc.calculate_total_payable()


def close_related_request(doc: ServiceReport, method: str | None = None) -> None:
    """Mark the linked Service Request as closed on submit."""

    if doc.service_request:
        frappe.db.set_value(
            "Service Request", doc.service_request, "status", STATUS_CLOSED
        )
