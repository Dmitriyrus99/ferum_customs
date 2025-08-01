# ferum_customs/patches/v1_0/rename_project_to_service_project.py
import frappe
from frappe.model.rename_doc import rename_doc

def execute() -> None:
    """Renames DocType 'Project' to 'Service Project' if needed."""
    if frappe.db.exists("DocType", "Project") and not frappe.db.exists(
        "DocType", "Service Project"
    ):
        print("Renaming DocType 'Project' to 'Service Project'...")
        try:
            rename_doc(
                "DocType",
                "Project",
                "Service Project",
                force=True,
                ignore_permissions=True,
            )
            print("Successfully renamed 'Project' to 'Service Project'.")
        except Exception as e:
            frappe.log_error(
                message=f"Error renaming DocType Project to Service Project: {e}", 
                title="Patch Error"
            )
            print(f"Error during rename: {e}")
    elif not frappe.db.exists("DocType", "Project"):
        print("DocType 'Project' does not exist. Skipping rename.")
    elif frappe.db.exists("DocType", "Service Project"):
        print("DocType 'Service Project' already exists. Skipping rename.")
