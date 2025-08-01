import importlib
from types import SimpleNamespace
from ferum_customs.constants import STATUS_OTKRYTA
from unittest.mock import MagicMock

def test_bot_create_and_update(frappe_stub: MagicMock) -> None:
    api = importlib.reload(importlib.import_module("ferum_customs.api"))

    calls = {}

    def get_doc(arg1: str, arg2: str = None) -> SimpleNamespace:
        if isinstance(arg1, dict):
            doc = SimpleNamespace(name="SR001")

            def insert(ignore_permissions: bool = True) -> None:
                calls["insert"] = arg1

            doc.insert = insert
            return doc
        if arg1 == "Service Request":
            doc = SimpleNamespace(status=None)

            def save(ignore_permissions: bool = True) -> None:
                calls["status"] = doc.status

            doc.save = save
            return doc
        raise AssertionError("unexpected get_doc args")

    frappe_stub.get_doc = get_doc
    sr_name = api.bot_create_service_request("Subj", customer="Cust")
    assert sr_name == "SR001"
    assert calls["insert"]["subject"] == "Subj"

    api.bot_update_service_request_status(sr_name, STATUS_OTKRYTA)
    assert calls["status"] == STATUS_OTKRYTA


def test_bot_upload_attachment(frappe_stub: MagicMock) -> None:
    api = importlib.reload(importlib.import_module("ferum_customs.api"))

    recorded = {}

    def get_doc(arg1: str, arg2: str = None) -> SimpleNamespace:
        if isinstance(arg1, dict):
            doc = SimpleNamespace(name="CA001")

            def insert(ignore_permissions: bool = True) -> None:
                recorded["doc"] = arg1

            doc.insert = insert
            return doc
        raise AssertionError("unexpected get_doc args")

    frappe_stub.get_doc = get_doc

    ca_name = api.bot_upload_attachment("SR001", "file.jpg", "photo")
    assert ca_name == "CA001"
    assert recorded["doc"]["parent_reference_sr"] == "SR001"
