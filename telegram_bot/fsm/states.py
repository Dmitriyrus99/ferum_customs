from aiogram.fsm.state import State, StatesGroup


class SomeState(StatesGroup):  # type: ignore[misc]
    """Example FSM state used in tests."""

    waiting = State()
