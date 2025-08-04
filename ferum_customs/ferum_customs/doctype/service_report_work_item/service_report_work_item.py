# Copyright (c) 2025 Ferum LLC and contributors
# For license information, please see license.txt

from frappe import _
from frappe.model.document import Document


class ServiceReportWorkItem(Document):
    """Represents a work item in a service report.
    This DocType is used to manage individual work items associated with service reports.

    Attributes:
        field_name (str): Description of the field.
        another_field (int): Description of another field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize any additional attributes if necessary

    def validate(self) -> None:
        """Override validate method to add custom validation logic."""
        super().validate()
        # Add validation logic here

    def on_update(self) -> None:
        """Override on_update method to add custom logic after updating the document."""
        super().on_update()
        # Add post-update logic here

    # Define fields here, e.g.:
    # field_name = frappe.db.Fieldtype.String()
    # another_field = frappe.db.Fieldtype.Int()
