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
"""

# --- Статусы Заявок на обслуживание (service_request) ---
# Эти значения должны совпадать со значениями в соответствующем Workflow
# или поле Select.
# Англоязычные варианты (если используются внутренне или для совместимости)
STATUS_OPEN: str = "Open"
STATUS_IN_PROGRESS: str = "In Progress"  # или "Working"
STATUS_ON_HOLD: str = "On Hold"
STATUS_COMPLETED: str = "Completed"
STATUS_CLOSED: str = "Closed"
STATUS_CANCELLED: str = "Cancelled"
STATUS_REJECTED: str = "Rejected"

# Русскоязычные варианты (основные для UI и бизнес-логики в данном приложении)
STATUS_OTKRYTA: str = "Открыта"  # Соответствует "Open" или начальному статусу
STATUS_V_RABOTE: str = "В работе"  # Соответствует "In Progress" / "Working"
STATUS_VYPOLNENA: str = (
    "Выполнена"  # Соответствует "Completed" (работа завершена инженером)
)
STATUS_ZAKRYTA: str = (
    "Закрыта"  # Соответствует "Closed" (финальный статус, подтверждено)
)
STATUS_OTMENENA: str = (
    "Отменена"  # Соответствует "Cancelled" (отменена инициатором или системой)
)

# Ordered list of valid statuses for Service Request workflow
SERVICE_REQUEST_STATUSES: tuple[str, ...] = (
    STATUS_OTKRYTA,
    STATUS_V_RABOTE,
    STATUS_VYPOLNENA,
    STATUS_ZAKRYTA,
    STATUS_OTMENENA,
)


# --- Роли Пользователей ---
# Эти значения должны совпадать с именами ролей, определенными в системе
# (Desk > Users > Role).
# Англоязычные варианты (если используются внутренне)
ROLE_SYSTEM_MANAGER: str = "System Manager"
ROLE_ADMINISTRATOR: str = "Administrator"  # Стандартная роль Frappe
ROLE_PROJECT_MANAGER: str = "Project Manager"  # Пример
ROLE_SERVICE_ENGINEER: str = "Service Engineer"  # Пример
ROLE_CUSTOMER: str = "Customer"  # Пример

# Русскоязычные варианты (основные для UI и бизнес-логики)
ROLE_PROEKTNYJ_MENEDZHER: str = "Проектный менеджер"  # Из fixtures/role.json
ROLE_INZHENER: str = "Инженер"  # Из fixtures/role.json
ROLE_ZAKAZCHIK: str = "Заказчик"  # Из fixtures/role.json


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
# Например, ключи для настроек, имена полей по умолчанию и т.д.
# DEFAULT_COMPANY: str = "Ferum LLC"
# MAX_LOGIN_ATTEMPTS: int = 5


# Список констант, которые считаются "публичным API" этого модуля.
# Помогает инструментам анализа и улучшает ясность относительно того,
# какие константы предназначены для использования в других частях приложения.
__all__ = [
    # Статусы
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
    # Роли
    "ROLE_SYSTEM_MANAGER",
    "ROLE_ADMINISTRATOR",
    "ROLE_PROJECT_MANAGER",
    "ROLE_SERVICE_ENGINEER",
    "ROLE_CUSTOMER",
    "ROLE_PROEKTNYJ_MENEDZHER",
    "ROLE_INZHENER",
    "ROLE_ZAKAZCHIK",
    # Типы вложений
    "ATTACHMENT_TYPE_PHOTO",
    "ATTACHMENT_TYPE_DOCUMENT",
    "ATTACHMENT_TYPE_OTHER",
    # Имена кастомных полей
    "FIELD_CUSTOM_CUSTOMER",
    "FIELD_CUSTOM_SERVICE_OBJECT_LINK",
    "FIELD_CUSTOM_ASSIGNED_ENGINEER",
    "FIELD_CUSTOM_PROJECT",
    "FIELD_CUSTOM_LINKED_REPORT",
    # Другие
    # "DEFAULT_COMPANY", "MAX_LOGIN_ATTEMPTS",
]

# Проверка, чтобы убедиться, что все экспортируемые имена действительно определены
# Это необязательно, но может помочь на этапе разработки
if __debug__:
    for _name in __all__:
        if _name not in globals():
            raise NameError(f"Constant '{_name}' listed in __all__ but not defined.")
