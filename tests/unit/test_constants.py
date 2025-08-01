from ferum_customs import constants

def test_constants_values():
    """Test the existence and type of constants in the constants module."""
    
    # List of constants to check
    constant_names = ['STATUS_OTKRYTA', 'STATUS_ZAKRYTA', 'STATUS_V_PROCESE']  # Add all relevant constants here
    
    for name in constant_names:
        assert hasattr(constants, name), f"{name} does not exist in constants"
        assert isinstance(getattr(constants, name), str), f"{name} is not a string"
