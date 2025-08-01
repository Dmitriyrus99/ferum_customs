"""Handlers for the Telegram bot.

This module contains the handlers that manage the interactions
with the Telegram bot, including starting the bot and managing
incident states.
"""

from .bot_service import IncidentStates, start_handler

__all__ = ["start_handler", "IncidentStates"]  # Expose the main handler and incident states for external use.
