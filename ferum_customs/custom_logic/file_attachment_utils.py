# ferum_customs/ferum_customs/custom_logic/file_attachment_utils.py
"""Утилиты для работы с файлами вложений.

Содержит функцию для безопасного удаления файлов вложений.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import frappe  # Frappe логгер интегрирован с системой
from frappe import _

if TYPE_CHECKING:
    from frappe.model.document import Document as FrappeDocument
else:  # pragma: no cover - provide fallback when Frappe is absent
    from typing import Any

    FrappeDocument = Any  # type: ignore

# Получаем экземпляр логгера Frappe для текущего модуля
logger = frappe.logger(__name__)


def _resolve_attachment_path(file_url: str, is_private: bool) -> tuple[Path, Path, str]:
    """Validate ``file_url`` and return the resolved attachment path, base dir and safe name."""
    base_folder = "private" if is_private else "public"
    prefix = f"/{base_folder}/files/" if is_private else "/files/"

    if not file_url.startswith(prefix):
        msg = (
            _("Некорректный URL приватного файла: {0}")
            if is_private
            else _("Некорректный URL публичного файла: {0}")
        )
        raise frappe.ValidationError(msg.format(file_url))

    relative = file_url[len(prefix) :]
    safe_name = os.path.basename(relative)
    if safe_name != relative or not safe_name or safe_name in (".", ".."):
        logger.error(
            "Path traversal attempt or invalid character in file_url '%s'. Original relative: '%s', Basename: '%s'",
            file_url,
            relative,
            safe_name,
        )
        raise frappe.PermissionError(
            _("Недопустимое имя файла или попытка обхода пути.")
        )

    base_dir = Path(frappe.get_site_path(base_folder, "files")).resolve(strict=True)
    file_path = (base_dir / safe_name).resolve()

    is_safe_path = (
        file_path.is_relative_to(base_dir)
        if hasattr(Path, "is_relative_to")
        else str(file_path).startswith(str(base_dir))
    )
    if not is_safe_path:
        logger.error(
            "Path traversal attempt or incorrect path resolution for attachment URL: '%s'. Resolved path: '%s', Base dir: '%s'",
            file_url,
            file_path,
            base_dir,
        )
        raise frappe.PermissionError(_("Неверный путь вложения. Доступ запрещен."))

    return file_path, base_dir, safe_name


@frappe.whitelist()
def delete_attachment_file_from_filesystem(
    file_url: str, is_private: bool = False
) -> None:
    """
    Безопасно удаляет физический файл из файловой системы.
    Предполагается, что этот метод вызывается, когда соответствующая запись "File" удаляется
    или когда "CustomAttachment" (или подобный DocType) удаляется.

    Args:
        file_url: URL файла (например, /files/myfile.jpg или /private/files/myfile.jpg).
        is_private: Флаг, указывающий, является ли файл приватным.

    Raises:
        frappe.ValidationError: Если `file_url` некорректный.
        frappe.DoesNotExistError: Если файл не найден.
        frappe.PermissionError: Если путь выходит за пределы разрешенной директории
                                 или происходит иная ошибка доступа.
    """
    if not file_url or not isinstance(file_url, str):
        logger.warning(
            "delete_attachment_file_from_filesystem: Invalid file_url provided: %s",
            file_url,
        )
        raise frappe.ValidationError(_("Некорректный URL файла вложения."))

    try:
        file_path, base_dir, safe_name = _resolve_attachment_path(file_url, is_private)
    except FileNotFoundError:
        logger.warning(
            "Base directory for attachments ('%s/files') not found or path is incorrect. Site path: '%s', File URL: '%s'",
            "private" if is_private else "public",
            frappe.get_site_path("private" if is_private else "public", "files"),
            file_url,
            exc_info=True,
        )
        return
    except Exception as e:
        logger.error(
            "Error resolving paths for attachment URL '%s': %s",
            file_url,
            e,
            exc_info=True,
        )
        raise frappe.PermissionError(
            _("Ошибка при определении пути к файлу. Обратитесь к администратору.")
        )

    if not file_path.exists():
        logger.info(
            f"File '{file_path}' (from URL '{file_url}') not found on filesystem. Nothing to delete."
        )
        # Это не ошибка, файл мог быть удален ранее.
        return

    if not file_path.is_file():
        logger.warning(
            f"Path '{file_path}' (from URL '{file_url}') is not a file. Skipping deletion."
        )
        # Не выбрасываем ошибку, но логируем.
        return

    try:
        file_path.unlink()
        logger.info(
            f"Successfully deleted attachment file: '{file_path}' (from URL '{file_url}') by user '{frappe.session.user}'"
        )
        # frappe.msgprint(_("Файл {0} успешно удален из файловой системы.").format(safe_name), alert=True, indicator="green") # Может быть излишним, если это фоновый процесс
    except OSError as e:
        logger.error(
            f"OS error while deleting file '{file_path}' (URL: '{file_url}') by user '{frappe.session.user}': {e}",
            exc_info=True,
        )
        frappe.throw(
            _(
                "Не удалось удалить файл {0} из файловой системы из-за системной ошибки. Обратитесь к администратору."
            ).format(safe_name),
            title=_("Ошибка удаления файла"),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while deleting file '{file_path}' (URL: '{file_url}') by user '{frappe.session.user}': {e}",
            exc_info=True,
        )
        frappe.throw(
            _(
                "Произошла непредвиденная ошибка при удалении файла {0} из файловой системы."
            ).format(safe_name),
            title=_("Ошибка удаления файла"),
        )


# Хук для DocType "CustomAttachment", который будет вызывать удаление файла
# Этот хук должен быть прописан в hooks.py:
# "CustomAttachment": {
#     "on_trash": "ferum_customs.custom_logic.file_attachment_utils.on_custom_attachment_trash"
# }
def on_custom_attachment_trash(doc: FrappeDocument, method: str | None = None):
    """
    Вызывается при удалении записи CustomAttachment (on_trash).
    Удаляет связанный физический файл и, если есть, запись File.

    Args:
        doc: Экземпляр документа CustomAttachment.
        method: Имя вызвавшего метода.
    """
    file_url = doc.get("attachment_file")  # Поле типа Attach хранит URL файла
    is_private_file = doc.get(
        "is_private", False
    )  # Предположим, есть поле 'is_private'

    if file_url:
        try:
            # 1. Удаляем физический файл
            delete_attachment_file_from_filesystem(file_url, is_private=is_private_file)

            # 2. Удаляем связанную запись DocType "File", если она существует
            # Это также удалит оптимизированные файлы и резервные копии, если они были созданы Frappe
            file_doc_name = frappe.db.get_value("File", {"file_url": file_url})
            if file_doc_name:
                frappe.delete_doc(
                    "File", file_doc_name, ignore_permissions=True, force_delete=True
                )
                logger.info(
                    f"Deleted File DocType record '{file_doc_name}' for CustomAttachment '{doc.name}' (URL: {file_url})."
                )
            else:
                logger.info(
                    f"No File DocType record found for URL '{file_url}' (CustomAttachment '{doc.name}'). Physical file was targeted for deletion."
                )

        except Exception as e:
            logger.error(
                f"Error during on_trash for CustomAttachment '{doc.name}' (file URL: {file_url}): {e}",
                exc_info=True,
            )
            # Не прерываем процесс удаления записи CustomAttachment, но логируем ошибку
            frappe.msgprint(
                _(
                    "Ошибка при удалении связанного файла для {0}. Файл мог остаться в системе. Сообщите администратору."
                ).format(doc.name),
                title=_("Ошибка удаления файла"),
                indicator="orange",
            )


# Пример хука для стандартного DocType "File", если требуется дополнительная логика.
# Этот хук должен быть прописан в hooks.py:
# "File": {
# "on_trash": "ferum_customs.custom_logic.file_attachment_utils.on_general_file_trash"
# }
# def on_general_file_trash(doc: "FrappeDocument", method: str | None = None):
# """
# Вызывается при удалении стандартной записи File (on_trash).
# Frappe обычно сам удаляет физический файл при удалении File DocType.
# Этот хук нужен, только если требуется *дополнительная* логика.
# """
# logger.info(f"Standard File DocType '{doc.name}' (URL: {doc.file_url}) is being trashed. Custom logic can be added here.")
# # Физический файл УЖЕ ДОЛЖЕН БЫТЬ удален стандартной логикой Frappe к этому моменту,
# # или будет удален сразу после этого хука.
# # Не нужно вызывать delete_attachment_file_from_filesystem(), если нет особых причин.
