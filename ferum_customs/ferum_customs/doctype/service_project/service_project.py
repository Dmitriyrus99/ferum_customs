# ferum_customs/ferum_customs/doctype/service_project/service_project.py
"""
Python-контроллер для DocType "Service Project".
"""

from __future__ import annotations

import datetime
from typing import Optional, cast

import frappe
from frappe import _
from frappe.model.document import Document


class ServiceProject(Document):
    """Класс документа Service Project."""

    def validate(self) -> None:
        """Валидация данных документа."""
        self._validate_dates()
        self._validate_budget()
        self._format_dates_to_iso()
        self._validate_unique_objects()

    def _validate_dates(self) -> None:
        """Проверяет корректность дат начала и окончания проекта.
        Даты должны быть объектами date/datetime для сравнения."""
        start_date_val: str | None = self.get("start_date")
        end_date_val: str | None = self.get("end_date")

        if start_date_val and end_date_val:
            try:
                start_dt = frappe.utils.get_date(start_date_val)
                end_dt = frappe.utils.get_date(end_date_val)

                if end_dt < start_dt:
                    frappe.throw(
                        _(
                            "Дата окончания проекта ({0}) не может быть раньше даты начала ({1})."
                        ).format(
                            frappe.utils.formatdate(end_dt),
                            frappe.utils.formatdate(start_dt),
                        )
                    )
            except Exception as e:
                frappe.logger(__name__).warning(
                    f"Could not validate dates for Service Project {self.name} due to parsing error: {e}"
                )

    def _format_dates_to_iso(self) -> None:
        """Форматирует поля дат в ISO формат, если они установлены и являются объектами date/datetime."""
        date_fields = ["start_date", "end_date"]
        for fieldname in date_fields:
            field_value = self.get(fieldname)
            if field_value and not isinstance(field_value, str):
                if isinstance(field_value, datetime.datetime | datetime.date):
                    try:
                        setattr(self, fieldname, field_value.isoformat())
                    except Exception as e:
                        frappe.logger(__name__).error(
                            f"Error converting date field '{fieldname}' to ISO format for Service Project '{self.name}': {e}"
                        )
            elif isinstance(field_value, str):
                try:
                    dt_obj = frappe.utils.get_datetime(field_value)
                    setattr(
                        self,
                        fieldname,
                        (
                            dt_obj.date().isoformat()
                            if isinstance(dt_obj, datetime.datetime)
                            else dt_obj.isoformat()
                        ),
                    )
                except Exception as e:
                    frappe.logger(__name__).warning(
                        f"Could not convert string date field '{fieldname}' to ISO format for Service Project '{self.name}': {e}"
                    )

    def _validate_budget(self) -> None:
        """Проверяет, что бюджет неотрицательный."""
        if self.get("budget") is not None:
            try:
                budget_val: float = float(self.budget)
                if budget_val < 0:
                    frappe.throw(_("Бюджет проекта не может быть отрицательным."))
            except (ValueError, TypeError):
                frappe.throw(_("Некорректное значение бюджета проекта."))

    def _validate_unique_objects(self) -> None:
        """Ensure each service object is linked to only one project."""
        objects_table: list[dict] = self.get("service_objects") or []
        seen: set[str] = set()
        for idx, row in enumerate(objects_table, start=1):
            obj = row.get("service_object")
            if not obj:
                frappe.throw(_("Service Object is required (row {0}).").format(idx))

            obj = cast(str, obj)
            if obj in seen:
                frappe.throw(
                    _("Service Object {0} is duplicated in this project.").format(obj)
                )
            seen.add(obj)

            existing_parent = frappe.db.get_value(
                "Project Object Item",
                {
                    "service_object": obj,
                    "parent": ["!=", self.name],
                },
                "parent",
            )
            if existing_parent:
                frappe.throw(
                    _("Service Object {0} is already linked to project {1}.").format(
                        obj, existing_parent
                    )
                )
