# Copyright (c) 2025 Ferum LLC and contributors
# For license information, please see license.txt

from frappe.model.document import Document

class ServiceReportDocumentItem(Document):
    """Represents an item in the service report document.

    This class currently does not implement any specific logic. 
    Frappe will use the standard behavior for child documents.
    If validation or other logic is needed, it can be added here.
    
    Attributes:
        item_code (str): The code of the item.
        quantity (int): The quantity of the item.
    """
    
    item_code: str
    quantity: int

    def validate(self) -> None:
        """Override the validate method to implement custom validation logic."""
        # Add validation logic here if needed
        pass
