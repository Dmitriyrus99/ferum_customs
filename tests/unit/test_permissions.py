from types import SimpleNamespace

import pytest

from ferum_customs.permissions.permissions import (
    ROLE_CUSTOMER,
    ROLE_ZAKAZCHIK,
    get_service_request_pqc,
)


@pytest.fixture
def frappe_stub(mocker):
    """Fixture to mock frappe functionalities."""
    mock = mocker.Mock()
    mock.session = SimpleNamespace()
    mock.has_role = mocker.Mock()
    mock.get_cached_doc = mocker.Mock()
    return mock


def test_get_service_request_pqc_for_customer(frappe_stub):
    """Test that a customer can retrieve their service request PQC."""
    frappe_stub.session.user = "alice"
    frappe_stub.has_role.side_effect = lambda role, user=None: role in {
        ROLE_CUSTOMER,
        ROLE_ZAKAZCHIK,
    }
    frappe_stub.get_cached_doc.return_value = SimpleNamespace(
        customer="CUST1",
        get=lambda field, default=None: {"customer": "CUST1"}.get(field, default),
    )

    pqc = get_service_request_pqc()
    assert pqc == {"custom_customer": "CUST1"}


def test_get_service_request_pqc_for_admin(frappe_stub):
    """Test that an admin cannot retrieve a service request PQC."""
    frappe_stub.session.user = "Administrator"
    frappe_stub.has_role.return_value = False
    frappe_stub.get_cached_doc.return_value = None

    assert get_service_request_pqc() is None
