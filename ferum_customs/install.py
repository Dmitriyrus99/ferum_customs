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

    # Role creation should be done through fixtures (fixtures/role.json).
    # Additional installation logic can be added as needed.

    # Example: Adding custom fields programmatically (usually done through fixtures/custom_field.json)
    # add_custom_fields()

    # Example: Setting up default permissions (usually done through fixtures/custom_docperm.json)
    # setup_default_permissions()

    # Example: Creating initial data
    # create_initial_data()

    frappe.db.commit()  # Final commit
    frappe.clear_cache()  # Clear cache after installation
    frappe.msgprint(
        _(
            "Ferum Customs application installed successfully. Please check system settings and user roles."
        ),
        title=_("Installation Complete"),
        indicator="green",
    )


# Example function for adding Custom Fields (not recommended, better through fixtures)
# def add_custom_fields() -> None:
#     if not frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "custom_user_department"}):
#         frappe.get_doc({
#             "doctype": "Custom Field",
#             "dt": "User",
#             "fieldname": "custom_user_department",
#             "label": "Department (Custom)",
#             "fieldtype": "Link",
#             "options": "Department",
#             "insert_after": "role_profile_name"  # Example
#         }).insert()

# Example function for creating initial data
# def create_initial_data() -> None:
#     if not frappe.db.exists("ServiceType", {"service_type_name": "Standard Maintenance"}):  # Example DocType
#         frappe.get_doc({
#             "doctype": "ServiceType",
#             "service_type_name": "Standard Maintenance",
#             "default_duration_hours": 2
#         }).insert()
