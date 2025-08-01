# ferum_customs/install.py
"""
Code executed after the installation of the `ferum_customs` application.

Can be used to create initial data, roles,
custom fields (though fixtures are preferred for this),
or other settings necessary for the application to function.
"""

import frappe
from frappe import _  # For possible messages


def after_install() -> None:
    """
    Called once after successful installation of the application.
    """
    # Ensure transactions are completed before starting operations in after_install
    if frappe.db.transaction_writes:
        frappe.db.commit()  # Commit previous transactions if necessary

    # Role creation and permissions setup should be done through fixtures.
    # Additional installation logic can be added as needed.

    # Example: Creating initial data
    create_initial_data()

    frappe.clear_cache()  # Clear cache after installation
    frappe.msgprint(
        _(
            "Ferum Customs application installed successfully. Please check system settings and user roles."
        ),
        title=_("Installation Complete"),
        indicator="green",
    )


def create_initial_data() -> None:
    """Create initial data for the application."""
    if not frappe.db.exists("ServiceType", {"service_type_name": "Standard Maintenance"}):  # Example DocType
        frappe.get_doc({
            "doctype": "ServiceType",
            "service_type_name": "Standard Maintenance",
            "default_duration_hours": 2
        }).insert()
