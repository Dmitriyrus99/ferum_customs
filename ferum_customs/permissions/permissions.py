# ferum_customs/permissions/permissions.py
"""
Динамические условия для запросов разрешений (Permission Query Conditions).
"""

from __future__ import annotations

from typing import Union

import frappe

from ferum_customs.constants import ROLE_CUSTOMER, ROLE_ZAKAZCHIK

PQCConditionValue = str | list[str | list[str]] | dict[str, str] | tuple[str, str]
PQCConditions = dict[str, PQCConditionValue]


def get_service_request_pqc(user: str | None = None) -> PQCConditions | None:
	if user is None:
		user = frappe.session.user

	if user == "Administrator" or frappe.has_role("System Manager", user):
		return None

	try:
		user_doc = frappe.get_cached_doc("User", user)
	except frappe.DoesNotExistError:
		frappe.logger(__name__).warning(f"User '{user}' not found while applying PQC for service_request.")
		return {"name": ("=", f"__no_records_user_not_found_{user}")}

	# Поле 'customer' в User DocType должно быть кастомным, если вы его используете для PQC.
	# Предположим, оно называется 'custom_linked_customer_for_user' в User.
	# user_linked_customer = user_doc.get("custom_linked_customer_for_user")
	# Если вы используете стандартное поле 'company' для привязки к клиенту (что нетипично) или другое, адаптируйте.
	# Для примера, если пользователь-заказчик привязан к документу Customer через поле 'party' (стандартное для Portal User)
	# или через кастомное поле 'customer' в User.
	user_linked_customer = user_doc.get(
		"customer"
	)  # Предполагаем, что в User есть поле 'customer' (Link to Customer)

	is_customer_role = frappe.has_role(ROLE_ZAKAZCHIK, user) or frappe.has_role(ROLE_CUSTOMER, user)

	if is_customer_role and user_linked_customer:
		# Пользователь с ролью "Заказчик" и привязанным клиентом видит только заявки своего клиента.
		# service_request теперь имеет поле custom_customer
		return {"custom_customer": user_linked_customer}

	return None
