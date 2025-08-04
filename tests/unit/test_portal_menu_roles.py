import json
from pathlib import Path
from typing import Any

FIXTURE_PATH = Path("ferum_customs/fixtures")


def load_fixture(name: str) -> list[dict[str, Any]]:
    file_path = FIXTURE_PATH / name
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file {name} does not exist.")
    content = file_path.read_text()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Fixture file {name} contains invalid JSON.")


def test_portal_menu_item_role_customer() -> None:
    """Test that all portal menu items have the role 'Customer' and not 'Guest'."""
    items = load_fixture("portal_menu_item.json")
    assert items, "portal_menu_item.json is empty"
    for item in items:
        assert "role" in item, f"Item is missing 'role' key: {item}"
        assert item["role"] == "Customer", f"Item role is not 'Customer': {item}"
        assert item["role"] != "Guest", f"Item role should not be 'Guest': {item}"


def test_no_guest_in_custom_docperm() -> None:
    """Test that 'Guest' role is not present in custom document permissions."""
    docperms = load_fixture("custom_docperm.json")
    roles: set[str] = {perm.get("role") for perm in docperms}
    assert "Guest" not in roles, "'Guest' role found in custom_docperm.json"
