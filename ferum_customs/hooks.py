# Ferum Customs - hooks
from ferum_customs.custom_hooks import DOC_EVENTS

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_publisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

doc_events = DOC_EVENTS
permission_query_conditions = {
	"Service Request": "ferum_customs.permissions.permissions.get_service_request_pqc",
}
get_notification_config = "ferum_customs.notifications.notifications.get_notification_config"

# ── актуальный список фикстур: только данные, без описаний DocType ──
fixtures = [
	"Custom Field",
	"Notification",
	"Portal Menu Item",
	"Role",
	"Custom Role",
	"Client Script",
	"DocPerm",
]


def scheduler_events() -> dict:
	"""Return scheduler events configuration for Frappe."""
	return {}


try:  # dev-hooks (если есть)
	from ferum_customs.dev_hooks import *
except ImportError:
	pass
