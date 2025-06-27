import importlib
from types import SimpleNamespace


def test_get_service_request_pqc_for_customer(frappe_stub):
    frappe_stub.session = SimpleNamespace(user="alice")
    permissions = importlib.import_module("ferum_customs.permissions.permissions")
    frappe_stub.has_role = lambda role, user=None: role in {
        permissions.ROLE_CUSTOMER,
        permissions.ROLE_ZAKAZCHIK,
    }
    frappe_stub.get_cached_doc = lambda doctype, name: SimpleNamespace(
        customer="CUST1",
        get=lambda field, default=None: {"customer": "CUST1"}.get(field, default),
    )

    importlib.reload(permissions)
    pqc = permissions.get_service_request_pqc()
    assert pqc == {"custom_customer": "CUST1"}


def test_get_service_request_pqc_for_admin(frappe_stub):
    frappe_stub.session = SimpleNamespace(user="Administrator")
    permissions = importlib.import_module("ferum_customs.permissions.permissions")
    frappe_stub.has_role = lambda role, user=None: False
    frappe_stub.get_cached_doc = lambda *a, **k: None

    importlib.reload(permissions)
    assert permissions.get_service_request_pqc() is None
