from ferum_customs import constants


def test_constants_values() -> None:
    """Test the existence, type, and values of constants in the constants module."""

    # List of constants to check
    constant_names: list[str] = [
        "STATUS_OTKRYTA",
        "STATUS_ZAKRYTA",
        "STATUS_V_PROCESE",
    ]  # Add all relevant constants here

    # Expected values for the constants
    expected_values = {
        "STATUS_OTKRYTA": "expected_value_1",  # Replace with actual expected value
        "STATUS_ZAKRYTA": "expected_value_2",  # Replace with actual expected value
        "STATUS_V_PROCESE": "expected_value_3",  # Replace with actual expected value
    }

    for name in constant_names:
        assert hasattr(constants, name), f"{name} does not exist in constants"
        assert isinstance(getattr(constants, name), str), f"{name} is not a string"
        assert (
            getattr(constants, name) == expected_values[name]
        ), f"{name} has an unexpected value"
