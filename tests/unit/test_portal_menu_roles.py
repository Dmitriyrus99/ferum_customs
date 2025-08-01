import json
from pathlib import Path
from typing import Any, List

FIXTURE_PATH = Path("ferum_customs/fixtures")


def load_fixture(name: str) -> Any:
    file_path = FIXTURE_PATH / name
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file {name} does not exist.")
    content = file_path.read_text()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Fixture file {name} contains invalid JSON.")


def test_portal_menu_item_role_customer() -> None:
    items = load_fixture("portal_menu_item.json")
    assert items, "portal_menu_item.json is empty"
    for item in items:
        assert item.get("role") == "Customer", f"Item role is not 'Customer': {item}"
        assert item.get("role") != "Guest", f"Item role should not be 'Guest': {item}"


def test_no_guest_in_custom_docperm() -> None:
    docperms = load_fixture("custom_docperm.json")
    roles: set = {perm.get("role") for perm in docperms}
    assert "Guest" not in roles, "'Guest' role found in custom_docperm.json"
