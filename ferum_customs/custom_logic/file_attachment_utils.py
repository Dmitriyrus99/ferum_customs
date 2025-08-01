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
    prefix = f"/{base_folder}/files/"

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

    if not str(file_path).startswith(str(base_dir)):
        logger.error(
            "Path traversal attempt or incorrect path resolution for attachment URL: '%s'. Resolved path: '%s', Base dir: '%s'",
            file_url,
            file_path,
            base_dir,
        )
        raise frappe.PermissionError(_("Неверный путь вложения. Доступ запрещен."))

    return file_path, base_dir, safe_name


@frappe.whitelist()  # type: ignore[misc]
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
        return

    if not file_path.is_file():
        logger.warning(
            f"Path '{file_path}' (from URL '{file_url}') is not a file. Skipping deletion."
        )
        return

    try:
        file_path.unlink()
        logger.info(
            f"Successfully deleted attachment file: '{file_path}' (from URL '{file_url}') by user '{frappe.session.user}'"
        )
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


def on_custom_attachment_trash(doc: FrappeDocument, method: str | None = None) -> None:
    """
    Вызывается при удалении записи CustomAttachment (on_trash).
    Удаляет связанный физический файл и, если есть, запись File.

    Args:
        doc: Экземпляр документа CustomAttachment.
        method: Имя вызвавшего метода.
    """
    file_url = doc.get("attachment_file")
    is_private_file = doc.get("is_private", False)

    if file_url:
        try:
            delete_attachment_file_from_filesystem(file_url, is_private=is_private_file)

            file_doc_name = frappe.db.get_value("File", {"file_url": file_url})
            if file_doc_name:
                frappe.delete_doc(
                    "File",
                    file_doc_name,
                    ignore_permissions=True,
                    force=True,
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
            frappe.msgprint(
                _(
                    "Ошибка при удалении связанного файла для {0}. Файл мог остаться в системе. Сообщите администратору."
                ).format(doc.name),
                title=_("Ошибка удаления файла"),
                indicator="orange",
            )
