import pytest
import os
from exbingads.client import Client
from exbingads.extractor import download_ad_performance_report
import datetime
import sys


def _make_client():
    cl = Client(
        developer_token=os.getenv("EX_DEVKEY"),
        client_id=os.getenv("EX_CLIENT_ID"),
        client_secret=os.getenv("EX_APP_SECRET"),
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
        predefinedTime='LastSevenDays'
        )
    if isinstance(out, str):
        assert os.stat(out).st_size > 0
    # can be None, which probably means there is no data to download
    # - maybe we might write an empty csv??

def test_client_download_report_predefined_time_sandbox(sbx):
    out = sbx.download_ad_performance_report(
        outdir='tests/sandbox/out/tables/',
        predefinedTime='LastSevenDays',
        completeData=False
        )
    assert os.stat(out).st_size > 0

def test_downloading_reports_with_predefined_day(sbx):
    """
    Scenario 1
    predefinedTime is set, everything else is ignored
    """
    config = {
        'predefinedTime': 'LastSevenDays',
        'completeData': False,
        'aggregation': 'Daily',
    }
    # since should be is ignored
    out = download_ad_performance_report(sbx, config, since_last='foobar', last_run=None,
                                      outdir='/tmp/exbingads_reports/predef')
    assert os.stat(out).st_size > 0


def test_downloading_reports_since_last_true(sbx):
    """
    Scenario 2

    no predefinedTime,
    since_last: True (takes start_date into account only the first time,
        all following start_dates are taken from statefile)

    """
    config = {
        'completeData': False,
        'aggregation': 'Daily',
        'startDate': datetime.datetime.strptime('10-10-2017', '%d-%m-%Y').date()
        # up until yesterday
    }
    out = download_ad_performance_report(sbx, config, since_last=True, last_run=None,
                                      outdir='/tmp/exbingads_reports/sl_true')
    assert os.stat(out).st_size > 0


def test_downloading_reports_since_last_true_last_run_second_run(sbx):
    """
    Scenario 3

    no predefinedTime,
    since_last: True (takes start_date into account only the first time,
        all following start_dates are taken from statefile)
    last

    """
    # 1 day after start_date
    last_run = datetime.datetime.strptime('11-10-2017', '%d-%m-%Y').date()
    config = {
        'completeData': False,
        'aggregation': 'Daily',
        'startDate': datetime.datetime.strptime('10-10-2017', '%d-%m-%Y').date()
        # up until yesterday
    }
    out = download_ad_performance_report(sbx,
                                         config,
                                         since_last=True,
                                         last_run=last_run,
                                         outdir='/tmp/exbingads_reports/sl_true_last_run')
    assert os.stat(out).st_size > 0


def test_downloading_reports_since_last_false(sbx):
    """
    Scenario 4

    no predefinedTime,
    since_last: False always download data from sinceLast to yesterday

    """
    config = {
        'completeData': False,
        'aggregation': 'Daily',
        'startDate': datetime.datetime.strptime('10-10-2017', '%d-%m-%Y').date()
        # up until yesterday
    }
    out = download_ad_performance_report(sbx, config, since_last=False, last_run=None,
                                      outdir='/tmp/exbingads_reports/sl_false')
    assert os.stat(out).st_size > 0
