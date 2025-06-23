# Ferum Customs - hooks
from .custom_hooks import DOC_EVENTS

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_publisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

doc_events = DOC_EVENTS
get_notification_config = "ferum_customs.notifications.notifications.get_notification_config"

# ── актуальный список фикстур: только данные, без описаний DocType ──
fixtures = [
        "custom_fields.json",
        "custom_docperm.json",
        "workflow_service_request.json",
        "portal_menu_item.json",
        "role.json",
        "notification.json",
        {"doctype": "DocType", "filters": [["name", "=", "ServiceReportWorkItem"]]},
]


def scheduler_events() -> dict:
	"""Return scheduler events configuration for Frappe."""
	return {}


try:  # dev-hooks (если есть)
	from .dev_hooks import *
except ImportError:
	pass
