from ferum_customs import constants

def test_constants_values():
    # Check if the attribute exists in the constants module
    assert hasattr(constants, 'STATUS_OTKRYTA'), "STATUS_OTKRYTA does not exist in constants"
    # Check if the attribute is a string
    assert isinstance(constants.STATUS_OTKRYTA, str), "STATUS_OTKRYTA is not a string"
