from datetime import datetime, timezone

import pytest
from aiogram import Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, Update

from telegram_bot.bot_service import IncidentStates, start_handler


@pytest.mark.asyncio
async def test_fsm_start_handler():
    bot = Bot(token="12345:TOKEN")
    storage = MemoryStorage()
    key = StorageKey(bot_id=bot.id or 0, chat_id=123, user_id=123)
    state = FSMContext(storage=storage, key=key)

    message = Message(
        message_id=1,
        date=datetime.now(timezone.utc),
        chat={"id": 123, "type": ChatType.PRIVATE},
        from_user={"id": 123, "is_bot": False, "first_name": "Tester"},
        text="/start",
    )
    update = Update(update_id=1, message=message)

    await start_handler(bot=bot, message=update.message, state=state)

    assert await state.get_state() == IncidentStates.waiting_object.state
