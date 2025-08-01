# ferum_customs/patches/v1_0/rename_project_to_service_project.py
import frappe
from frappe.model.rename_doc import rename_doc
from frappe import _

def execute() -> None:
    """Renames DocType 'Project' to 'Service Project' if needed."""
    if frappe.db.exists("DocType", "Project") and not frappe.db.exists("DocType", "Service Project"):
        frappe.logger().info("Renaming DocType 'Project' to 'Service Project'...")
        try:
            rename_doc(
                "DocType",
                "Project",
                "Service Project",
                force=True,
                ignore_permissions=True,
            )
            frappe.logger().info("Successfully renamed 'Project' to 'Service Project'.")
        except Exception as e:
            frappe.log_error(
                message=f"Error renaming DocType Project to Service Project: {e}", 
                title="Patch Error"
            )
            frappe.throw(_("Error during rename: {0}").format(e))
    elif not frappe.db.exists("DocType", "Project"):
        frappe.logger().info("DocType 'Project' does not exist. Skipping rename.")
    elif frappe.db.exists("DocType", "Service Project"):
        frappe.logger().info("DocType 'Service Project' already exists. Skipping rename.")
