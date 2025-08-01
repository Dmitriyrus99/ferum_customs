from aiogram.fsm.state import State, StatesGroup


class SomeState(StatesGroup):
    """Example FSM state used in tests.

    This state represents a waiting state in the finite state machine (FSM).
    It can be used to manage user interactions in a bot. This state is typically
    used when the bot is awaiting a response from the user.
    """

    waiting: State = State()
