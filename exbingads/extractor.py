from exbingads.utils import (write_manifest, parse_config,
                             parse_statefile, write_statefile)
from exbingads.client import Client
import os
import logging
import datetime
import csv


def main(datadir):
    params = parse_config(datadir)
    client = Client(
        developer_token=params['#devKey'],
        client_id=params.get('client_id', 'dummy'),
        refresh_token=params.get('refresh_token'),
        access_token=params.get('access_token'),
        client_secret=params.get('client_secret'),
        customer_id=params['customerId'],
        account_id=params['accountId'],
        environment='production'
    )

    final_outdir = os.path.join(datadir, 'out/tables')
    # Download the ads performance report

    since_last = params.get('sinceLast', False)
    state = parse_statefile(datadir)
    last_run = state.get('lastRun')
    if last_run:
        last_run = datetime.datetime.strptime(last_run, '%Y-%m-%d').date()
    for report_conf in params.get('reportRequests'):
        if report_conf['type'] == 'AdsPerformance':
            dl_params = parse_config_to_download_params(report_conf,
                                                          since_last,
                                                          last_run,
                                                          outdir=final_outdir)
            report_path = client.ad_performance_report(**dl_params)
            write_manifest(report_path,
                            params.get('bucket'),
                            table='AdsPerformance',
                            incremental=params.get('incremental', False),
                            pk_columns=report_conf.get('pkey')
            )

        if report_conf['type'] == 'KeywordPerformance':
            dl_params = parse_config_to_download_params(report_conf,
                                                        since_last,
                                                        last_run,
                                                        outdir=final_outdir)
            report_path = client.keyword_performance_report(**dl_params)
            write_manifest(report_path,
                            params.get('bucket'),
                            table='KeywordPerformance',
                            incremental=params.get('incremental', False),
                            pk_columns=report_conf.get('pkey')
            )
    new_state = state.copy()
    new_state['lastRun'] = str(datetime.datetime.now().date())
    write_statefile(datadir, new_state)

def parse_config_to_download_params(
        config,
        since_last,
        last_run,
        outdir='/data/out/tables'):
    """
    Decide how to download the report based on config

    Handle the time logic related to downloads

    The reports are at first downloaded to outdir (tmp dir in this case, since
    we will process them later on)

    if predefinedDate is specified, do that
    elif check statefile if the ex was ran
        if not and sinceLast is defined, download based on sinceLast and save today the new date in statefile.
        elif ex was ran already and sinceLast is defined, use the value from statefile

    elif startDate and endDate is specified, download that
    """
    download_params = {
        'completeData': config.get('completeData', True),
        'outdir': outdir,
        'predefinedTime': None,
        'startDate': None,
        'endDate': None,
        'columns': config.get('columns'),
        'aggregation': config.get('aggregation', 'Daily')
    }

    predefined_time = config.get('predefinedTime')
    if predefined_time:
        # predefined date, rule them all, you don't really care about anything
        download_params['predefinedTime'] = predefined_time
    elif since_last:
        # if the ex was already ran before, download data from that point onwards
        if last_run:
            start_date = last_run
        else:
            # The ex is a virgin
            try:
                start_date = config['startDate']
            except KeyError:
                raise ValueError("When setting sinceLast parameter, you must"
                                 "also define startDate")
        download_params['startDate'] = start_date
        end_date = config.get('end_date')
        download_params['endDate'] = end_date
    elif not since_last:
        # do not take into account the last_run parameter,
        # but just download the <start_date; end_date>
        try:
            start_date = config['startDate']
        except KeyError:
            raise ValueError("When setting sinceLast parameter, you must"
                             "also define startDate")
        download_params['startDate'] = start_date
        end_date = config.get('endDate')
        download_params['endDate'] = end_date

    else:
        raise ValueError(
            "Not sure what to do. config: %s"
            "since_last %s"
            "last_run %s", config, since_last, last_run)
    return download_params


def download_ad_performance_report(
        client,
        config,
        since_last,
        last_run,
        outdir='/data/out/tables'):
    """
    Download teh AdPerformance report
    """
    download_params = parse_config_to_download_params(config, since_last, last_run, outdir)
    report_path = client.ad_performance_report(**download_params)
    return report_path


def download_keyword_performance_report(
        client,
        config,
        since_last,
        last_run,
        outdir='/data/out/tables'):
    """
    Download teh KeywordPerformance report
    """
    download_params = parse_config_to_download_params(config, since_last, last_run, outdir)
    report_path = client.keyword_performance_report(**download_params)
    return report_path
