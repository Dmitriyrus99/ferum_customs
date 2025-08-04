import sys
import types
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

# Provide minimal aiogram stubs so tests can run without the real library
if "aiogram" not in sys.modules:
    aiogram = types.ModuleType("aiogram")

    class Bot:
        def __init__(self, token: str) -> None:
            self.token = token
            self.id = 1

    aiogram.Bot = Bot

    class Dispatcher:
        def __init__(self, *, storage: "BaseStorage", bot: Bot) -> None:
            self.storage = storage
            self.bot = bot

    aiogram.Dispatcher = Dispatcher

    enums = types.ModuleType("aiogram.enums")
    enums.ChatType = types.SimpleNamespace(PRIVATE="private")
    sys.modules["aiogram.enums"] = enums
    aiogram.enums = enums

    storage_base = types.ModuleType("aiogram.fsm.storage.base")

    class StorageKey:
        def __init__(self, bot_id: int, chat_id: int, user_id: int) -> None:
            self.bot_id = bot_id
            self.chat_id = chat_id
            self.user_id = user_id

    class BaseStorage(dict):
        pass

    storage_base.StorageKey = StorageKey
    storage_base.BaseStorage = BaseStorage
    sys.modules["aiogram.fsm.storage.base"] = storage_base

    storage_memory = types.ModuleType("aiogram.fsm.storage.memory")

    class MemoryStorage(dict):
        pass

    storage_memory.MemoryStorage = MemoryStorage
    sys.modules["aiogram.fsm.storage.memory"] = storage_memory

    fsm_context = types.ModuleType("aiogram.fsm.context")

    class FSMContext:
        def __init__(self, storage: BaseStorage, key: StorageKey) -> None:
            self._storage = storage
            self._key = key

        async def set_state(self, state: Any) -> None:
            value = getattr(state, "state", state)
            self._storage[self._key] = value

        async def get_state(self) -> Any:
            return self._storage.get(self._key)

    fsm_context.FSMContext = FSMContext
    sys.modules["aiogram.fsm.context"] = fsm_context

    fsm_state = types.ModuleType("aiogram.fsm.state")

    class State:
        def __set_name__(self, owner: Any, name: str) -> None:
            self.state = f"{owner.__name__}:{name}"

    class StatesGroup:
        pass

    fsm_state.State = State
    fsm_state.StatesGroup = StatesGroup
    sys.modules["aiogram.fsm.state"] = fsm_state

    aiogram.fsm = types.SimpleNamespace(
        context=fsm_context,
        storage=types.SimpleNamespace(memory=storage_memory, base=storage_base),
        state=fsm_state,
    )

    types_mod = types.ModuleType("aiogram.types")

    class Message(dict):
        pass

    class Update:
        def __init__(self, update_id: int, message: Message) -> None:
            self.update_id = update_id
            self.message = message

    types_mod.Message = Message
    types_mod.Update = Update
    sys.modules["aiogram.types"] = types_mod
    aiogram.types = types_mod

    sys.modules["aiogram"] = aiogram


class DummyLog:
    def info(self, *args: Any, **kwargs: Any) -> None:
        pass

    def warning(self, *args: Any, **kwargs: Any) -> None:
        pass

    def error(self, *args: Any, **kwargs: Any) -> None:
        pass


@pytest.fixture
def frappe_stub(monkeypatch, tmp_path):
    frappe = types.SimpleNamespace()
    frappe.db = types.SimpleNamespace(
        exists=lambda *args, **kwargs: None,
        get_value=lambda *args, **kwargs: None,
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
    frappe.throw = lambda msg, exc=None, *args, **kwargs: (_ for _ in ()).throw(
        exc(msg) if exc else ValidationError(msg)
    )
    frappe._ = lambda s: s
    frappe.logger = lambda name=None: DummyLog()
    frappe.utils = types.SimpleNamespace(now=lambda: "now")
    frappe.get_site_path = lambda *parts: str(tmp_path.joinpath(*parts))
    frappe.session = types.SimpleNamespace(user="test-user")
    frappe.whitelist = lambda *args, **kwargs: (lambda f: f)
    frappe.get_doc = lambda *args, **kwargs: None
    frappe.get_all = lambda *args, **kwargs: []
    frappe.has_permission = lambda *args, **kwargs: True
    sys.modules["frappe"] = frappe
    yield frappe
    sys.modules.pop("frappe", None)
