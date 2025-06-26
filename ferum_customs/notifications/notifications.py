# ferum_customs/notifications/notifications.py
"""
Конфигурация уведомлений для приложения `ferum_customs`.

Эта функция `get_notification_config` должна быть указана в `hooks.py`:
`notification_config = "ferum_customs.notifications.notifications.get_notification_config"`

Возвращает словарь, описывающий условия для отправки стандартных уведомлений Frappe.
"""

from frappe import _  # Для перевода возможных строк в будущем

# Импорт констант для статусов, если они используются в условиях
from ..constants import ROLE_PROEKTNYJ_MENEDZHER, STATUS_OTKRYTA, STATUS_V_RABOTE


def get_notification_config() -> dict:
	"""
	Возвращает конфигурацию для стандартных уведомлений Frappe.
	"""
	return {
		"Service Request": {
			# Отправлять уведомление, только если статус изменился.
			"condition": ("doc.get_doc_before_save() and doc.status != doc.get_doc_before_save().status"),
			# Получатели уведомлений
			"send_to_roles": [ROLE_PROEKTNYJ_MENEDZHER],
			# Темы и сообщения можно шаблонизировать через Jinja
			"subject": _("Статус заявки {{ doc.name }} изменён на {{ doc.status }}"),
			"message": _(
				"""
Здравствуйте!

Заявка <strong>{{ doc.name }}</strong> изменила статус на
<strong>{{ doc.status }}</strong>.
{% if doc.custom_customer %}Клиент: {{ frappe.get_cached_value("Customer", doc.custom_customer, "customer_name") or doc.custom_customer }} {% endif %}
{% if doc.custom_assigned_engineer %}Назначенный инженер: {{ frappe.get_cached_value("User", doc.custom_assigned_engineer, "full_name") or doc.custom_assigned_engineer }} {% endif %}

Открыть заявку: {{ frappe.utils.get_link_to_form('Service Request', doc.name) }}

--
Система Ferum Customs
"""
			),
		},
		# "ServiceReport": { # Пример для другого DocType
		#     "condition": "doc.docstatus == 1", # Отправлять при отправке (submit) ServiceReport
		#     "send_to_roles": [ROLE_PROEKTNYJ_MENEDZHER],
		#     "subject": _("Отчет о выполненных работах {{ doc.name }} был отправлен"),
		#     "message": _("Отчет {{ doc.name }} для заявки {{ doc.service_request }} был отправлен.") # service_request - стандартное поле в ServiceReport
		# }
	}
