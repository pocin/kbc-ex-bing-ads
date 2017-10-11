import pytest
import os
from exbingads.client import Client


def _make_client():
    cl = Client(
        developer_token=os.getenv("EX_DEVKEY"),
        client_id=os.getenv("EX_CLIENT_ID"),
        refresh_token=os.getenv('EX_REFRESH_TOKEN'),
        customer_id=os.getenv('EX_CUSTOMER_ID'),
        account_id=os.getenv('EX_ACCOUNT_ID'),
        environment='production'
    )
    return cl

def test_authenticating_client():
    cl = _make_client()
    assert cl.refresh_token is not None

@pytest.fixture
def client():
    return _make_client()

# def test_client_download_report():
#     pass

