from aiogram.fsm.state import State, StatesGroup


class SomeState(StatesGroup):
	"""Example FSM state used in tests."""

	waiting = State()
