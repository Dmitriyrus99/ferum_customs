import pytest
from ferum_customs.custom_logic import file_attachment_utils

def test_resolve_attachment_public(frappe_stub, tmp_path):
    public_files_path = tmp_path / "public" / "files"
    public_files_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    path, base, name = file_attachment_utils._resolve_attachment_path("/files/test.txt", False)
    assert path == public_files_path / "test.txt"
    assert base == public_files_path
    assert name == "test.txt"

def test_resolve_attachment_invalid_prefix(frappe_stub):
    with pytest.raises(frappe_stub.ValidationError):
        file_attachment_utils._resolve_attachment_path("/bad/test.txt", False)

def test_resolve_attachment_traversal(frappe_stub, tmp_path):
    public_files_path = tmp_path / "public" / "files"
    public_files_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with pytest.raises(frappe_stub.PermissionError):
        file_attachment_utils._resolve_attachment_path("/files/../secret.txt", False)
