import importlib
import os
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


@pytest.fixture
def bot() -> Bot:
    """Fixture to create a Bot instance."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set.")
    return Bot(token=token, parse_mode="HTML")


@pytest.fixture
def storage() -> MemoryStorage:
    """Fixture to create a MemoryStorage instance."""
    return MemoryStorage()


@pytest.mark.asyncio
async def test_start_handler_sets_incident_state(bot: Bot, storage: MemoryStorage):
    """Test that start_handler sets the FSM to the correct state."""
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


def test_get_dispatcher_custom_bot_and_storage(bot: Bot, storage: MemoryStorage):
    """Test that get_dispatcher returns the provided bot and storage objects."""
    dp = get_dispatcher(bot=bot, storage=storage)
    assert dp.bot is bot
    assert dp.storage is storage
