import importlib

import pytest


def get_utils():
	return importlib.import_module("ferum_customs.custom_logic.file_attachment_utils")


def test_resolve_attachment_public(frappe_stub, tmp_path):
	(tmp_path / "public" / "files").mkdir(parents=True)
	utils = importlib.reload(get_utils())
	path, base, name = utils._resolve_attachment_path("/files/test.txt", False)
	assert path == (tmp_path / "public" / "files" / "test.txt").resolve()
	assert base == (tmp_path / "public" / "files").resolve()
	assert name == "test.txt"


def test_resolve_attachment_invalid_prefix(frappe_stub):
	utils = importlib.reload(get_utils())
	with pytest.raises(frappe_stub.ValidationError):
		utils._resolve_attachment_path("/bad/test.txt", False)


def test_resolve_attachment_traversal(frappe_stub, tmp_path):
	(tmp_path / "public" / "files").mkdir(parents=True)
	utils = importlib.reload(get_utils())
	with pytest.raises(frappe_stub.PermissionError):
		utils._resolve_attachment_path("/files/../secret.txt", False)
