import importlib
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest
from aiogram import Bot

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from aiogram import types as aiogram_types
else:
    aiogram_types = importlib.import_module("aiogram.types")
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from telegram_bot.bot_service import IncidentStates, get_dispatcher, start_handler


@pytest.mark.asyncio
async def test_start_handler_sets_incident_state():
    """Проверяем, что start_handler переводит FSM в нужное состояние."""
    bot = Bot(token="test-token", parse_mode=None)  # Ensure parse_mode is explicitly set
    storage = MemoryStorage()
    key = StorageKey(bot_id=bot.id or 0, chat_id=123, user_id=123)
    state = FSMContext(storage=storage, key=key)
    message = cast(
        aiogram_types.Message,
        SimpleNamespace(
            message_id=1,
            date=datetime.now(timezone.utc),
            chat=SimpleNamespace(id=123, type=ChatType.PRIVATE),
            from_user=SimpleNamespace(id=123, is_bot=False, first_name="Tester"),
            text="/start",
        ),
    )
    await start_handler(bot=bot, message=message, state=state)
    assert await state.get_state() == IncidentStates.waiting_object.state


def test_get_dispatcher_custom_bot_and_storage():
    """Проверяем, что get_dispatcher возвращает переданные объекты bot и storage."""
    bot = Bot(token="test-token", parse_mode=None)  # Ensure parse_mode is explicitly set
    storage = MemoryStorage()
    dp = get_dispatcher(bot=bot, storage=storage)
    assert dp.bot is bot
    assert dp.storage is storage
