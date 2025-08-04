import pytest

from ferum_customs.custom_logic import file_attachment_utils


def test_resolve_attachment_public(frappe_stub, tmp_path) -> None:
    """Test resolving a public attachment path."""
    public_files_path = tmp_path / "public" / "files"
    public_files_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    path, base, name = file_attachment_utils._resolve_attachment_path(
        "/files/test.txt", False
    )
    assert path == public_files_path / "test.txt"
    assert base == public_files_path
    assert name == "test.txt"


def test_resolve_attachment_invalid_prefix(frappe_stub) -> None:
    """Test resolving an attachment path with an invalid prefix raises ValidationError."""
    with pytest.raises(frappe_stub.ValidationError):
        file_attachment_utils._resolve_attachment_path("/bad/test.txt", False)


def test_resolve_attachment_traversal(frappe_stub, tmp_path) -> None:
    """Test resolving an attachment path with traversal attempts raises PermissionError."""
    public_files_path = tmp_path / "public" / "files"
    public_files_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with pytest.raises(frappe_stub.PermissionError):
        file_attachment_utils._resolve_attachment_path("/files/../secret.txt", False)


def test_resolve_attachment_file_not_exist(frappe_stub, tmp_path) -> None:
    """Test resolving a valid attachment path that does not exist."""
    public_files_path = tmp_path / "public" / "files"
    public_files_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    path, base, name = file_attachment_utils._resolve_attachment_path(
        "/files/nonexistent.txt", False
    )
    assert path == public_files_path / "nonexistent.txt"
    assert base == public_files_path
    assert name == "nonexistent.txt"
