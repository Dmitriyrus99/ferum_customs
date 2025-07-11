import pytest
from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage

from telegram_bot.bot_service import IncidentStates, get_dispatcher, start_handler


class DummyState:
    """Заготовка FSMContext для тестирования start_handler."""

    def __init__(self):
        self.states = []

    async def set_state(self, state):
        self.states.append(state)


@pytest.mark.asyncio
async def test_start_handler_sets_incident_state():
    """Проверяем, что start_handler переводит FSM в нужное состояние."""
    dummy = DummyState()
    await start_handler(bot=None, message=None, state=dummy)
    assert dummy.states == [IncidentStates.waiting_object]


def test_get_dispatcher_custom_bot_and_storage():
    """Проверяем, что get_dispatcher возвращает переданные объекты bot и storage."""
    bot = Bot(token="test-token")
    storage = MemoryStorage()
    dp = get_dispatcher(bot=bot, storage=storage)
    assert dp.bot is bot
    assert dp.storage is storage
