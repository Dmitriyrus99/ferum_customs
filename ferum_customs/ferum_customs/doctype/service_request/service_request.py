# ferum_customs/ferum_customs/doctype/service_request/service_request.py
"""
Python-контроллер для DocType "Service Request".
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime

if TYPE_CHECKING:
    from frappe.types import DF


class ServiceRequest(Document):
    # Аннотации типов для полей DocType
    subject: DF.Data
    status: DF.Data
    custom_customer: DF.Link | None
    custom_service_object_link: DF.Link | None
    custom_project: DF.Link | None
    request_datetime: DF.Datetime
    completed_on: DF.Datetime | None
    planned_start_datetime: DF.Datetime | None
    planned_end_datetime: DF.Datetime | None
    actual_start_datetime: DF.Datetime | None
    actual_end_datetime: DF.Datetime | None
    duration_hours: DF.Float

    def validate(self) -> None:
        """Валидация документа перед сохранением."""
        self._clean_fields()
        self._validate_dates()

    def before_save(self) -> None:
        """Действия перед сохранением документа."""
        self._calculate_duration()
        self._autofill_project_from_service_object()

    def on_submit(self) -> None:
        """Действия при отправке документа."""
        if not self.actual_start_datetime:
            self.db_set("actual_start_datetime", frappe.utils.now_datetime())

    def _clean_fields(self) -> None:
        """Очистка и нормализация полей."""
        if self.subject:
            self.subject = self.subject.strip()

    def _validate_dates(self) -> None:
        """Проверка корректности временных интервалов."""
        date_pairs = [
            ("planned_start_datetime", "planned_end_datetime", "Планируемый"),
            ("actual_start_datetime", "actual_end_datetime", "Фактический"),
        ]

        for start_field, end_field, label in date_pairs:
            start_val, end_val = self.get(start_field), self.get(end_field)
            if start_val and end_val:
                if get_datetime(start_val) > get_datetime(end_val):
                    frappe.throw(
                        _(
                            "{0} период: дата начала не может быть позже даты окончания."
                        ).format(label)
                    )

    def _calculate_duration(self) -> None:
        """Расчет длительности работ в часах."""
        if self.actual_start_datetime and self.actual_end_datetime:
            try:
                start_dt = get_datetime(self.actual_start_datetime)
                end_dt = get_datetime(self.actual_end_datetime)
                if end_dt >= start_dt:
                    duration = (end_dt - start_dt).total_seconds() / 3600.0
                    self.duration_hours = round(duration, 2)
                else:
                    self.duration_hours = 0.0
            except (TypeError, ValueError) as e:
                frappe.logger(__name__).warning(
                    f"Не удалось рассчитать длительность для заявки {self.name}: {e}"
                )
                self.duration_hours = 0.0

    def _autofill_project_from_service_object(self) -> None:
        """Автозаполнение проекта из связанного объекта обслуживания."""
        if self.custom_service_object_link and not self.custom_project:
            project = frappe.db.get_value(
                "Service Object",
                self.custom_service_object_link,
                "linked_service_project",
            )
            if project:
                self.custom_project = project
