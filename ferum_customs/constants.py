# ferum_customs/constants.py
"""
Единый набор констант, используемых во всём приложении `ferum_customs`.

Содержит как англоязычные (наследие ERPNext, если применимо, или для
внутреннего использования),
так и русскоязычные идентификаторы статусов, ролей и других перечислимых
значений,
используемых в бизнес-логике и UI.

Использование констант вместо "магических строк" улучшает читаемость,
сопровождаемость и уменьшает вероятность ошибок из-за опечаток.

Примеры использования:
- Используйте STATUS_OPEN для проверки статуса заявки.
- Используйте ROLE_ADMINISTRATOR для проверки прав доступа пользователя.
"""

from typing import List

# --- Статусы Заявок на обслуживание (service_request) ---
STATUS_OPEN: str = "Open"
STATUS_IN_PROGRESS: str = "In Progress"  # или "Working"
STATUS_ON_HOLD: str = "On Hold"
STATUS_COMPLETED: str = "Completed"
STATUS_CLOSED: str = "Closed"
STATUS_CANCELLED: str = "Cancelled"
STATUS_REJECTED: str = "Rejected"

STATUS_OTKRYTA: str = "Открыта"
STATUS_V_RABOTE: str = "В работе"
STATUS_VYPOLNENA: str = "Выполнена"
STATUS_ZAKRYTA: str = "Закрыта"
STATUS_OTMENENA: str = "Отменена"

SERVICE_REQUEST_STATUSES: List[str] = [
    STATUS_OTKRYTA,
    STATUS_V_RABOTE,
    STATUS_VYPOLNENA,
    STATUS_ZAKRYTA,
    STATUS_OTMENENA,
]

# --- Роли Пользователей ---
ROLE_SYSTEM_MANAGER: str = "System Manager"
ROLE_ADMINISTRATOR: str = "Administrator"
ROLE_PROJECT_MANAGER: str = "Project Manager"
ROLE_SERVICE_ENGINEER: str = "Service Engineer"
ROLE_CUSTOMER: str = "Customer"

ROLE_PROEKTNYJ_MENEDZHER: str = "Проектный менеджер"
ROLE_INZHENER: str = "Инженер"
ROLE_ZAKAZCHIK: str = "Заказчик"

# --- Типы вложений (CustomAttachment) ---
ATTACHMENT_TYPE_PHOTO: str = "photo"
ATTACHMENT_TYPE_DOCUMENT: str = "document"
ATTACHMENT_TYPE_OTHER: str = "other"

# --- Имена кастомных полей ---
FIELD_CUSTOM_CUSTOMER: str = "custom_customer"
FIELD_CUSTOM_SERVICE_OBJECT_LINK: str = "custom_service_object_link"
FIELD_CUSTOM_ASSIGNED_ENGINEER: str = "custom_assigned_engineer"
FIELD_CUSTOM_PROJECT: str = "custom_project"
FIELD_CUSTOM_LINKED_REPORT: str = "custom_linked_report"

# --- Другие константы ---
import os

DEFAULT_COMPANY: str = os.getenv("DEFAULT_COMPANY", "Ferum LLC")
MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))

__all__ = [
    "STATUS_OPEN",
    "STATUS_IN_PROGRESS",
    "STATUS_ON_HOLD",
    "STATUS_COMPLETED",
    "STATUS_CLOSED",
    "STATUS_CANCELLED",
    "STATUS_REJECTED",
    "STATUS_OTKRYTA",
    "STATUS_V_RABOTE",
    "STATUS_VYPOLNENA",
    "STATUS_ZAKRYTA",
    "STATUS_OTMENENA",
    "SERVICE_REQUEST_STATUSES",
    "ROLE_SYSTEM_MANAGER",
    "ROLE_ADMINISTRATOR",
    "ROLE_PROJECT_MANAGER",
    "ROLE_SERVICE_ENGINEER",
    "ROLE_CUSTOMER",
    "ROLE_PROEKTNYJ_MENEDZHER",
    "ROLE_INZHENER",
    "ROLE_ZAKAZCHIK",
    "ATTACHMENT_TYPE_PHOTO",
    "ATTACHMENT_TYPE_DOCUMENT",
    "ATTACHMENT_TYPE_OTHER",
    "FIELD_CUSTOM_CUSTOMER",
    "FIELD_CUSTOM_SERVICE_OBJECT_LINK",
    "FIELD_CUSTOM_ASSIGNED_ENGINEER",
    "FIELD_CUSTOM_PROJECT",
    "FIELD_CUSTOM_LINKED_REPORT",
]

if __debug__:
    for _name in __all__:
        if _name not in globals():
            raise NameError(f"Constant '{_name}' listed in __all__ but not defined.")
