# ferum_customs/ferum_customs/doctype/service_report/service_report.py
"""
Python controller for DocType "Service Report".
"""

from __future__ import annotations

import datetime
from typing import Optional, List, Dict

import frappe
from frappe import _
from frappe.model.document import Document


class ServiceReport(Document):
    service_request: Optional[str] = None
    customer: Optional[str] = None
    total_quantity: float = 0.0
    total_payable: float = 0.0

    def onload(self) -> None:
        pass

    def validate(self) -> None:
        self._clean_fields()
        self._validate_work_items()
        self._set_customer_from_service_request()
        self.calculate_totals()

    def before_save(self) -> None:
        pass  # Removed duplicate call to calculate_totals

    def on_submit(self) -> None:
        pass

    def _clean_fields(self) -> None:
        if self.service_request and isinstance(self.service_request, str):
            self.service_request = self.service_request.strip()

        if self.customer and isinstance(self.customer, str):
            self.customer = self.customer.strip()

        posting_date_val = self.get("posting_date")
        if posting_date_val:
            if not isinstance(posting_date_val, str):
                if isinstance(posting_date_val, (datetime.datetime, datetime.date)):
                    self.posting_date = posting_date_val.isoformat()
        else:
            if self.is_new() and self.meta.get_field("posting_date").reqd:
                self.posting_date = frappe.utils.nowdate()

    def _validate_work_items(self) -> None:
        work_items_table: List[Dict] = self.get("work_items") or []
        if not work_items_table:
            return

        for idx, item in enumerate(work_items_table):
            row_num = idx + 1
            description = item.get("description", "").strip()
            if not description:
                frappe.throw(
                    _("Description is required for all work items (row {0}).").format(row_num)
                )
            item["description"] = description

            if item.get("quantity") is not None and item["quantity"] < 0:
                frappe.throw(
                    _("Quantity cannot be negative (row {0}).").format(row_num)
                )
            if item.get("unit_price") is not None and item["unit_price"] < 0:
                frappe.throw(
                    _("Unit price cannot be negative (row {0}).").format(row_num)
                )

    def _set_customer_from_service_request(self) -> None:
        if self.service_request and not self.customer:
            try:
                customer_from_sr = frappe.db.get_value(
                    "Service Request", self.service_request, "custom_customer"
                )

                if customer_from_sr:
                    self.customer = customer_from_sr
                else:
                    frappe.logger(__name__).warning(
                        f"Customer not found in linked Service Request '{self.service_request}' (field custom_customer) for ServiceReport '{self.name}'."
                    )
            except Exception as e:
                frappe.logger(__name__).error(
                    f"Error setting customer from service_request '{self.service_request}' for ServiceReport '{self.name}': {e}",
                    exc_info=True,
                )

    def calculate_totals(self) -> None:
        total_qty: float = 0.0
        total_pay: float = 0.0

        work_items_table: List[Dict] = self.get("work_items", [])

        for item in work_items_table:
            try:
                qty = float(item.get("quantity", 0.0) or 0.0)
                price = float(item.get("unit_price", 0.0) or 0.0)
            except (ValueError, TypeError):
                qty = 0.0
                price = 0.0
                frappe.logger(__name__).warning(
                    f"Invalid numeric value for quantity or unit_price in work_items for SR {self.name}, item idx {item.get('idx')}"
                )

            item["quantity"] = round(qty, 2)
            item["unit_price"] = round(price, 2)

            amount = round(item["quantity"] * item["unit_price"], 2)
            item["amount"] = amount

            total_qty += item["quantity"]
            total_pay += item["amount"]

        self.total_quantity = round(total_qty, 2)
        self.total_payable = round(total_pay, 2)

    def create_sales_invoice(self) -> str:
        """Create a Sales Invoice draft for this report."""
        from ferum_customs import api

        self.calculate_totals()
        return str(api.create_invoice_from_report(self.name))
