import pytest
from ferum_customs import constants

def test_constants_values():
    assert isinstance(constants.APP_NAME, str)
