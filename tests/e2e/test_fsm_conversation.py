import pytest
from aiogram.types import Update
from telegram_bot.bot_service import get_dispatcher

@pytest.mark.asyncio
async def test_fsm_mock_conversation():
    dispatcher = get_dispatcher()
    update = Update(update_id=1, message={"text": "/start"})
    assert dispatcher
