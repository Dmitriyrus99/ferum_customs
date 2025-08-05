"""DocType hook mapping used by hooks.py."""

from typing import Any

DOC_EVENTS: dict[str, dict[str, str]] = {
    "Service Request": {
        "validate": "ferum_customs.custom_logic.service_request_hooks.validate",
        "on_update_after_submit": "ferum_customs.custom_logic.service_request_hooks.on_update_after_submit",
        "on_trash": "ferum_customs.custom_logic.service_request_hooks.prevent_deletion_with_links",
    },
    "Service Report": {
        "validate": "ferum_customs.custom_logic.service_report_hooks.validate",
        "before_save": "ferum_customs.custom_logic.service_report_hooks.calculate_total_payable",
        "on_submit": "ferum_customs.custom_logic.service_report_hooks.close_related_request",
    },
    "Service Object": {
        "validate": "ferum_customs.custom_logic.service_object_hooks.validate",
        "on_trash": "ferum_customs.custom_logic.service_object_hooks.prevent_deletion_with_active_requests",
    },
    "Payroll Entry Custom": {
        "validate": "ferum_customs.custom_logic.payroll_entry_hooks.validate",
        "before_save": "ferum_customs.custom_logic.payroll_entry_hooks.before_save",
    },
    "Custom Attachment": {
        "on_trash": "ferum_customs.custom_logic.file_attachment_utils.on_custom_attachment_trash",
    },
}
