# Ferum Customs – hooks
from .custom_hooks import DOC_EVENTS

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_publisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

doc_events = DOC_EVENTS
get_notification_config = "ferum_customs.notifications.notifications.get_notification_config"

# ── порядок фикстур: сначала DocType, затем поля/права, затем данные ──
fixtures = [
	"service_request.json",
	"service_object.json",
	"service_project.json",
	"custom_fields.json",
	"custom_docperm.json",
	"audit_log.json",
	"workflow_service_request.json",
	"portal_menu_item.json",
	"role.json",
	"notification.json",
	"users.json",
	"customer.json",
]


def scheduler_events() -> dict:
	"""Return scheduler events configuration for Frappe."""
	return {}


try:  # dev-hooks (если есть)
	from .dev_hooks import *  # noqa
except ImportError:
	pass
