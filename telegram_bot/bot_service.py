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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
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


def _create_dispatcher(
    bot: Bot | None = None,
    storage: BaseStorage | None = None,
) -> Dispatcher:
    """Instantiate dispatcher with in‑memory storage."""

    if bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "0:TOKEN")
        bot = Bot(token)
    if storage is None:
        storage = MemoryStorage()
    return Dispatcher(storage=storage, bot=bot)


def get_dispatcher(
    *, bot: Bot | None = None, storage: BaseStorage | None = None
) -> Dispatcher:
    """Return a dispatcher instance for external usage (e.g. tests)."""

    return _create_dispatcher(bot=bot, storage=storage)


dispatcher = _create_dispatcher()


async def start_handler(bot: Bot, message: Message, state: FSMContext) -> None:
    """Simple `/start` command handler.

    It sets the incident FSM to the first state. Network calls are omitted
    for testing purposes.
    """

    await state.set_state(IncidentStates.waiting_object)


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
    "get_dispatcher",
    "start_handler",
    "IncidentStates",
    "TaskStates",
    "PhotoStates",
]
