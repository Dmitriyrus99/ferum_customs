import sys
import types

import pytest


class DummyLog:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


@pytest.fixture
def frappe_stub(monkeypatch):
    frappe = types.SimpleNamespace()
    frappe.db = types.SimpleNamespace(
        exists=lambda *a, **k: None,
        get_value=lambda *a, **k: None,
    )

    class ValidationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    frappe.ValidationError = ValidationError
    frappe.PermissionError = PermissionError
    exc_mod = types.ModuleType("frappe.exceptions")
    exc_mod.PermissionError = PermissionError
    sys.modules["frappe.exceptions"] = exc_mod
    frappe.DoesNotExistError = Exception
    frappe.throw = lambda msg, exc=None, *a, **k: (_ for _ in ()).throw(
        exc(msg) if exc else ValidationError(msg)
    )
    frappe._ = lambda s: s
    frappe.logger = lambda name=None: DummyLog()
    frappe.utils = types.SimpleNamespace(now=lambda: "now")
    frappe.whitelist = lambda *args, **kwargs: (lambda f: f)
    frappe.get_doc = lambda *a, **k: None
    frappe.get_all = lambda *a, **k: []
    frappe.has_permission = lambda *a, **k: True
    sys.modules["frappe"] = frappe
    yield frappe
    sys.modules.pop("frappe", None)
