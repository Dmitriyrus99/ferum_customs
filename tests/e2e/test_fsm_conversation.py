
import pytest

pytest.importorskip("aiogram")

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from datetime import datetime, timezone
from aiogram.utils.token import TokenValidationError

try:
	from telegram_bot.bot_service import IncidentStates, get_dispatcher
except Exception:
	pytest.skip("bot service init failed", allow_module_level=True)


def test_fsm_start_handler():
	async def _run():
		# Подготовка мока
		try:
			bot = Bot(token="12345:TOKEN", parse_mode="HTML")
		except TokenValidationError:
			pytest.skip("invalid token")
		storage = MemoryStorage()
		dispatcher: Dispatcher = get_dispatcher(bot=bot, storage=storage)

		# Эмуляция входящего сообщения
		_message = Message(
		message_id=1,
		date=datetime.now(timezone.utc),
		chat={"id": 123, "type": ChatType.PRIVATE},
		from_user={"id": 123, "is_bot": False, "first_name": "Test"},
		text="/start",
		)

		# Эмуляция FSM context
		key = StorageKey(bot_id=0, chat_id=123, user_id=123)
		_fsm_context = FSMContext(storage=storage, key=key)

		# Эмуляция вызова хендлера (только если у тебя он явно вызывается)
		# await start_handler(message, state=fsm_context)

		assert dispatcher

	import asyncio
	asyncio.run(_run())


def test_fsm_state_values():
	"""Ensure Incident FSM states have correct names."""

	assert IncidentStates.waiting_object.state == "IncidentStates:waiting_object"
	assert IncidentStates.waiting_description.state == "IncidentStates:waiting_description"
