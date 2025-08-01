from telegram_bot.fsm.states import SomeState

def test_dummy_fsm():
    # Ensure FSM states are accessible
    assert hasattr(SomeState, "waiting"), "SomeState should have an attribute 'waiting'"
