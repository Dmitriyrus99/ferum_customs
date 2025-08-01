# ferum_customs/ferum_customs/custom_logic/service_request_hooks.py
"""Hooks for DocType *Service Request*."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

import frappe
from frappe import _
from frappe.utils import get_link_to_form, now

from ferum_customs.constants import (
    FIELD_CUSTOM_CUSTOMER,
    FIELD_CUSTOM_LINKED_REPORT,
    FIELD_CUSTOM_PROJECT,
    FIELD_CUSTOM_SERVICE_OBJECT_LINK,
    ROLE_PROEKTNYJ_MENEDZHER,
    STATUS_VYPОЛНЕНА,
    STATUS_ZAKRYTA,
)

if TYPE_CHECKING:
    from frappe.model.document import Document as FrappeDocument
    from ferum_customs.ferum_customs.doctype.service_request.service_request import (
        ServiceRequest,
    )


# --------------------------------------------------------------------------- #
#                               Doc Events                                  #
# --------------------------------------------------------------------------- #


def validate(doc: ServiceRequest, method: Optional[str] = None) -> None:
    """Validate ``Service Request`` before saving."""
    if doc.status == STATUS_VYPОЛНЕНА and not doc.get(FIELD_CUSTOM_LINKED_REPORT):
        frappe.throw(_("Cannot mark the request as completed without a linked report."))

    if doc.status == STATUS_VYPОЛНЕНА and not doc.get("completed_on"):
        doc.completed_on = now()

    _ensure_customer(doc)


def on_update_after_submit(doc: ServiceRequest, method: Optional[str] = None) -> None:
    """Triggered after updating a submitted document."""
    if doc.status == STATUS_ZAKRYTA:
        _notify_project_manager(doc)


def prevent_deletion_with_links(doc: ServiceRequest, method: Optional[str] = None) -> None:
    """Prevents deletion of the request if there are links to it."""
    if linked_report := frappe.db.exists(
        "Service Report", {"service_request": doc.name}
    ):
        frappe.throw(
            _("Cannot delete request {0} as it is referenced by report {1}.").format(
                doc.name, linked_report
            )
        )


def _ensure_customer(doc: ServiceRequest) -> None:
    """Populate ``custom_customer`` field from project or service object."""
    if doc.get(FIELD_CUSTOM_CUSTOMER):
        return

    project = doc.get(FIELD_CUSTOM_PROJECT)
    if project:
        customer = frappe.db.get_value("Service Project", project, "customer")
        if customer:
            doc.custom_customer = customer
        else:
            frappe.throw(
                _("The selected project ({0}) has no associated customer.").format(
                    project
                )
            )
        return

    service_object = doc.get(FIELD_CUSTOM_SERVICE_OBJECT_LINK)
    if service_object:
        customer = frappe.db.get_value("Service Object", service_object, "customer")
        if customer:
            doc.custom_customer = customer


# --------------------------------------------------------------------------- #
#                           Whitelisted Methods                             #
# --------------------------------------------------------------------------- #


@frappe.whitelist(allow_guest=False)
def get_engineers_for_object(service_object_name: str) -> List[str]:
    """Returns a list of engineers assigned to the service object."""
    if not service_object_name:
        return []

    try:
        so_doc: FrappeDocument = frappe.get_doc("Service Object", service_object_name)
        engineers_table = so_doc.get("assigned_engineers") or []
        return list(
            {
                entry.get("engineer")
                for entry in engineers_table
                if entry.get("engineer")
            }
        )
    except frappe.DoesNotExistError:
        frappe.logger(__name__).info(
            f"Object '{service_object_name}' not found while searching for engineers."
        )
        return []
    except Exception as e:
        frappe.logger(__name__).error(
            f"Error retrieving engineers for object '{service_object_name}': {e}",
            exc_info=True,
        )
        return []


# --------------------------------------------------------------------------- #
#                               Helper Functions                             #
# --------------------------------------------------------------------------- #


def _notify_project_manager(doc: ServiceRequest) -> None:
    """Sends a notification about the closure of the request to project managers."""
    try:
        recipients = frappe.get_all(
            "User",
            filters={"enabled": 1, "roles.role": ROLE_PROEKTNYJ_MENEDZHER},
            pluck="name",
            distinct=True,
        )

        customer_email = doc.get("customer_email")
        if customer_email:
            recipients.append(customer_email)
        else:
            frappe.logger(__name__).warning(
                f"Service Request '{doc.name}' has no customer_email field set"
            )

        if not recipients:
            frappe.logger(__name__).warning(
                _("No recipients with role '{0}' found for notification.").format(
                    ROLE_PROEKTNYJ_MENEDZHER
                )
            )
            return

        subject = _("Service Request {0} Closed").format(doc.name)
        customer_name = (
            frappe.get_cached_value("Customer", doc.custom_customer, "customer_name")
            if doc.custom_customer
            else ""
        )

        message = _(
            """
            <p>Service request <b>{doc_name}</b> has been marked as 'Closed'.</p>
            <p>Subject: {subject}</p>
            <p>Customer: {customer}</p>
            <p><a href="{link}">{link_text}</a></p>
            """
        ).format(
            doc_name=doc.name,
            subject=doc.subject,
            customer=customer_name or _("Not specified"),
            link=get_link_to_form("Service Request", doc.name),
            link_text=_("View Request"),
        )

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype="Service Request",
            reference_name=doc.name,
            now=True,
        )
    except Exception as e:
        frappe.logger(__name__).error(
            f"Failed to send closure notification for request '{doc.name}': {e}",
            exc_info=True,
        )
