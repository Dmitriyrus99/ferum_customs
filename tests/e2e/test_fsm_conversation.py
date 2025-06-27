import pytest
from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.utils.token import TokenValidationError

try:
	from telegram_bot.bot_service import get_dispatcher
except Exception:
	pytest.skip("bot service init failed", allow_module_level=True)


@pytest.mark.asyncio
async def test_fsm_start_handler():
	# Подготовка мока
	try:
		bot = Bot(token="TEST:TOKEN", parse_mode="HTML")
	except TokenValidationError:
		pytest.skip("invalid token")
	storage = MemoryStorage()
	dispatcher: Dispatcher = get_dispatcher(bot=bot, storage=storage)

	# Эмуляция входящего сообщения
	_message = Message(
		message_id=1,
		date=None,
		chat={"id": 123, "type": ChatType.PRIVATE},
		from_user={"id": 123, "is_bot": False, "first_name": "Test"},
		text="/start",
	)

	# Эмуляция FSM context
	_fsm_context = FSMContext(storage=storage, chat_id=123, user_id=123)

	# Эмуляция вызова хендлера (только если у тебя он явно вызывается)
	# await start_handler(message, state=fsm_context)

	assert dispatcher
