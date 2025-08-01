# ferum_customs/custom_logic/file_attachment_utils.py
"""Utilities for working with file attachments.

Contains functions for safely deleting attachment files and handling related operations.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import frappe  # Frappe logger integrated with the system
from frappe import _

if TYPE_CHECKING:
    from frappe.model.document import Document as FrappeDocument
else:  # pragma: no cover - provide fallback when Frappe is absent
    from typing import Any

    FrappeDocument = Any  # type: ignore

# Get the Frappe logger instance for the current module
logger = frappe.logger(__name__)


def _resolve_attachment_path(file_url: str, is_private: bool) -> tuple[Path, Path, str]:
    """Validate ``file_url`` and return the resolved attachment path, base dir and safe name."""
    base_folder = "private" if is_private else "public"
    prefix = f"/{base_folder}/files/"

    if not file_url.startswith(prefix):
        msg = (
            _("Invalid private file URL: {0}")
            if is_private
            else _("Invalid public file URL: {0}")
        )
        raise frappe.ValidationError(msg.format(file_url))

    relative = file_url[len(prefix):]
    safe_name = os.path.basename(relative)
    if safe_name != relative or not safe_name or safe_name in (".", ".."):
        logger.error(
            "Path traversal attempt or invalid character in file_url '%s'. Original relative: '%s', Basename: '%s'",
            file_url,
            relative,
            safe_name,
        )
        raise frappe.PermissionError(
            _("Invalid file name or path traversal attempt.")
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
        raise frappe.PermissionError(_("Invalid attachment path. Access denied."))

    return file_path, base_dir, safe_name


@frappe.whitelist()
def delete_attachment_file_from_filesystem(
    file_url: str, is_private: bool = False
) -> None:
    """
    Safely deletes a physical file from the filesystem.
    This method is expected to be called when the corresponding "File" record is deleted
    or when "CustomAttachment" (or similar DocType) is deleted.

    Args:
        file_url: File URL (e.g., /files/myfile.jpg or /private/files/myfile.jpg).
        is_private: Flag indicating whether the file is private.

    Raises:
        frappe.ValidationError: If `file_url` is invalid.
        frappe.DoesNotExistError: If the file is not found.
        frappe.PermissionError: If the path goes beyond the allowed directory
                                 or if another access error occurs.
    """
    if not file_url or not isinstance(file_url, str):
        logger.warning(
            "delete_attachment_file_from_filesystem: Invalid file_url provided: %s",
            file_url,
        )
        raise frappe.ValidationError(_("Invalid attachment file URL."))

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
            _("Error determining file path. Please contact the administrator.")
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
                "Failed to delete file {0} from the filesystem due to a system error. Please contact the administrator."
            ).format(safe_name),
            title=_("File Deletion Error"),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while deleting file '{file_path}' (URL: '{file_url}') by user '{frappe.session.user}': {e}",
            exc_info=True,
        )
        frappe.throw(
            _(
                "An unexpected error occurred while deleting file {0} from the filesystem."
            ).format(safe_name),
            title=_("File Deletion Error"),
        )


def on_custom_attachment_trash(doc: FrappeDocument, method: Optional[str] = None) -> None:
    """
    Called when a CustomAttachment record is deleted (on_trash).
    Deletes the associated physical file and, if present, the File record.

    Args:
        doc: Instance of the CustomAttachment document.
        method: Name of the calling method.
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
                    "Error deleting associated file for {0}. The file may remain in the system. Please inform the administrator."
                ).format(doc.name),
                title=_("File Deletion Error"),
                indicator="orange",
            )
