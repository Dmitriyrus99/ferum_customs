import json
from pathlib import Path

# Compute absolute path to fixtures so tests work regardless of CWD
FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "ferum_customs" / "fixtures"
)


def load_fixture(name: str):
	return json.loads((FIXTURE_PATH / name).read_text())


def test_portal_menu_item_role_customer():
	items = load_fixture("portal_menu_item.json")
	assert items, "portal_menu_item.json is empty"
	for item in items:
		assert item["role"] == "Customer"
		assert item["role"] != "Guest"


def test_no_guest_in_custom_docperm():
	docperms = load_fixture("custom_docperm.json")
	roles = {perm["role"] for perm in docperms}
	assert "Guest" not in roles
