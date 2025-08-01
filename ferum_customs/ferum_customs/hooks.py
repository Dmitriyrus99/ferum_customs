# Ferum Customs - hooks
from typing import Any, Dict  # Import Dict for type hinting
from ferum_customs.custom_hooks import DOC_EVENTS
from ferum_customs.bench_commands.run_tests import run_tests

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_publisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

# Explicitly define doc_events for clarity
doc_events = {
    "Service Request": {
        "on_update": "ferum_customs.custom_hooks.on_service_request_update",
        "on_delete": "ferum_customs.custom_hooks.on_service_request_delete",
    },
    # Add other DocTypes and their events as needed
}

permission_query_conditions = {
    "Service Request": "ferum_customs.permissions.permissions.get_service_request_pqc",
}

get_notification_config = "ferum_customs.notifications.notifications.get_notification_config"

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
def get_bench_commands() -> Dict[str, Any]:
    return [
        {
            "command": run_tests,
            "description": "Run custom tests for Ferum Customs"
        },
    ]

def scheduler_events() -> Dict[str, Any]:  # Use Dict for type hinting
    """Return scheduler events configuration for Frappe."""
    return {
        "cron": {
            "0 * * * *": [
                "ferum_customs.tasks.run_scheduled_task"
            ]
        }
    }

try:  # dev-hooks (если есть)
    from ferum_customs.dev_hooks import *  # Avoid wildcard imports
except ImportError:
    pass
