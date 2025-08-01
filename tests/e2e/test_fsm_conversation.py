import importlib
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest
from aiogram import Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from telegram_bot.handlers import IncidentStates, start_handler

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from aiogram import types as aiogram_types
else:
    aiogram_types = importlib.import_module("aiogram.types")

@pytest.mark.asyncio
async def test_fsm_start_handler():
    """Test the start handler of the FSM to ensure it transitions to the correct state."""
    
    bot_token = "12345:TOKEN"  # Replace with a method to retrieve from environment
    bot = Bot(token=bot_token)
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

    # Clean up resources
    await bot.session.close()
