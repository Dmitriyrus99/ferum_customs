"""Minimal Telegram bot service using FastAPI and Aiogram.

This module provides a skeleton implementation of a webhook compatible
service.  The bot uses Finite State Machines (FSM) for different flows:

* ``IncidentStates`` – reporting incidents.
* ``TaskStates`` – creating new tasks.
* ``PhotoStates`` – uploading photos.

It can be extended further to react to Telegram updates and call the
whitelisted API methods defined in :mod:`ferum_customs.api`.
"""

from __future__ import annotations

import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI


class IncidentStates(StatesGroup):
	"""Conversation flow for incident reporting."""

	waiting_object = State()
	waiting_description = State()
	waiting_photo = State()


class TaskStates(StatesGroup):
	"""Conversation flow for task creation."""

	waiting_title = State()
	waiting_details = State()


class PhotoStates(StatesGroup):
	"""Standalone photo upload flow."""

	waiting_photo = State()
	confirming = State()


app = FastAPI(title="Ferum Bot Service")


def _create_dispatcher() -> Dispatcher:
	"""Instantiate dispatcher with in‑memory storage."""

	token = os.getenv("TELEGRAM_BOT_TOKEN", "")
	bot = Bot(token)
	return Dispatcher(storage=MemoryStorage(), bot=bot)


dispatcher = _create_dispatcher()


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - example implementation
	"""Hook that runs on service startup."""

	# Dispatcher can include routers with handlers here.
	pass


@app.on_event("shutdown")
async def shutdown_event() -> None:  # pragma: no cover - example implementation
	"""Hook that runs on service shutdown."""

	await dispatcher.storage.close()


__all__ = [
	"app",
	"dispatcher",
	"IncidentStates",
	"TaskStates",
	"PhotoStates",
]
