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
    {
        "doctype": "DocType",
        "filters": [["name", "=", "Service Report Work Item"]],
    },
]


def scheduler_events() -> dict:
	"""Return scheduler events configuration for Frappe."""
	return {}


try:  # dev-hooks (если есть)
	from .dev_hooks import *
except ImportError:
	pass
