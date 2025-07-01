import importlib
from types import SimpleNamespace


def test_create_invoice_from_report(frappe_stub):
	api = importlib.reload(importlib.import_module("ferum_customs.api"))

	sr_doc = SimpleNamespace(
		get=lambda key, default=None: {
			"customer": "Cust1",
			"work_items": [{"description": "Work", "quantity": 2, "unit_price": 50, "amount": 100}],
		}.get(key, default),
		calculate_totals=lambda: None,
	)

	items: list[dict] = []
	invoice_doc = SimpleNamespace(
		name="INV001",
		append=lambda field, item: items.append(item),
		insert=lambda ignore_permissions=True: None,
	)

	def get_doc(doctype, name=None):
		if isinstance(doctype, dict):
			return invoice_doc
		if doctype == "Service Report":
			assert name == "SR1"
			return sr_doc
		raise AssertionError("unexpected doctype")

	frappe_stub.get_doc = get_doc
	frappe_stub.db.exists = lambda *a, **k: None

	result = api.create_invoice_from_report("SR1")
	assert result == "INV001"
	assert items and items[0]["description"] == "Work"
