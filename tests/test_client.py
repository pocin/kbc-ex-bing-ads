import pytest
import os
from exbingads.client import Client
import sys


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

def _make_sandbox_client():
    return Client(developer_token='foobar',
                  client_id=os.getenv("EX_CLIENT_ID"),
                  _username=os.getenv("EX_SBX_USERNAME"),
                  _password=os.getenv("EX_SBX_PASSWD"),
                  _devkey=os.getenv("EX_SBX_DEVKEY"),
                  environment='sandbox'
    )

@pytest.fixture
def sbx():
    return _make_sandbox_client()

def test_authenticating_client():
    cl = _make_client()
    assert cl.refresh_token is not None

@pytest.fixture
def client():
    return _make_client()

def test_client_download_report_predefined_time(client):

    out = client.download_ad_performance_report(
        outdir='tests/data/out/tables/',
        predefined_time='LastSevenDays'
        )
    if isinstance(out, str):
        assert os.stat(out).st_size > 0
    # can be None, which probably means there is no data to download
    # - maybe we might write an empty csv??

def test_client_download_report_predefined_time_sandbox(sbx):
    out = sbx.download_ad_performance_report(
        outdir='tests/sandbox/out/tables/',
        predefined_time='LastSevenDays',
        complete_data=False
        )
    assert os.stat(out).st_size > 0
