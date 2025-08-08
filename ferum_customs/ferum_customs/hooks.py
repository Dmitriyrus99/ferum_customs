# Ferum Customs - hooks
from typing import Any

from ferum_customs.bench_commands.run_tests import run_tests
from ferum_customs.custom_hooks import DOC_EVENTS

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_publisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

# Explicitly define doc_events for clarity
doc_events = {
    "ServiceRequest": {
        "on_submit": "ferum_customs.notifications.send_telegram_notification"
    }
}

permission_query_conditions = {
    "Service Request": "ferum_customs.permissions.permissions.get_service_request_pqc",
}

get_notification_config = (
    "ferum_customs.notifications.notifications.get_notification_config"
)

# Fixtures for the app
fixtures = [
    "Custom Field",
    "Notification",
    "Portal Menu Item",
    "Role",
    "Custom Role",
    "Client Script",
    "DocPerm",
]


# Bench commands: custom CLI tools for this app
def get_bench_commands() -> list[dict[str, Any]]:
    return [
        {"command": run_tests, "description": "Run custom tests for Ferum Customs"},
    ]


def scheduler_events() -> dict[str, Any]:  # Use Dict for type hinting
    """Return scheduler events configuration for Frappe."""
    return {"cron": {"0 * * * *": ["ferum_customs.tasks.run_scheduled_task"]}}


try:  # dev-hooks (если есть)
    from ferum_customs.dev_hooks import *  # Avoid wildcard imports
except ImportError:
    pass
