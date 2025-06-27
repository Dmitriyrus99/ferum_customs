import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from telegram_bot.fsm.states import SomeState  # замените на ваше состояние
from telegram_bot.handlers import start_handler  # замените на ваш обработчик

class MockMessage(Message):
    def __init__(self):
        super().__init__(message_id=1, chat={"id": 123}, date=None, text="/start")

@pytest.mark.asyncio
async def test_fsm_start_handler():
    bot = Bot(token="TEST:TOKEN")
    dp = Dispatcher(storage=MemoryStorage())
    message = MockMessage()
    state: FSMContext = dp.storage.get_state(chat=message.chat.id, user=message.from_user.id)

    await start_handler(message, state=state)

    assert await state.get_state() == SomeState.some_step  # замените на ожидаемое состояние
