from bingads.service_client import ServiceClient
from bingads.authorization import *
from bingads.v11.bulk import *
from bingads.v11.reporting import *
import sys
import webbrowser
import json
from time import gmtime, strftime
import datetime
from suds import WebFault
import datetime
from hashlib import md5
from exbingads.utils import log_soap_errors, AuthenticationError

import logging
logging.basicConfig(level=logging.INFO)


class AuthClient:
    def __init__(self,
                 developer_token,
                 client_id,
                 client_secret=None,
                 refresh_token=None,
                 customer_id=None,
                 account_id=None,
                 environment='production',
                 _username=None, # for sandbox use
                 _password=None,
                 _devkey=None):
        """
        This class only manages authentication and you generally dont need to use
        it, rather use the Client child class

        For use in keboola (non-interactive) you must supply refresh token (OAuth bundle manages this)
        otherwise you will be prompted for user consent which is interactive.

        Args:
            developer_token: get from https://developers.bingads.microsoft.com/Account
            client_id: the registered app id from MS https://apps.dev.microsoft.com/#/application/
            refresh_token: (optional) if you have one, otherwise the next step will trigger OAuth webbrowser flow
            customer_id: # https://bingads.microsoft.com/cc/accounts
            account_id: # https://bingads.microsoft.com/cc/accounts

        """
        self._refresh_token = refresh_token
        self._environment = environment
        self._username = _username
        self._password = _password
        self.client_secret=client_secret,
        self._devkey = _devkey
        self.client_id = client_id
        if not isinstance(account_id, list):
            # None for sandbox purposes
            if isinstance(account_id, (str, int, type(None))):
                account_id = [account_id]
            else:
                raise ValueError("account_id must be a list of accountIds, not '{}'".format(account_id))
        self.account_id = account_id
        self.customer_id = customer_id
        self.CLIENT_STATE = md5(str(datetime.datetime.now()).encode(
            'utf-8')).hexdigest()

        self.authorization_data = AuthorizationData(
            account_id=account_id,
            customer_id=customer_id,
            developer_token=developer_token,
            authentication=None)

    def _authenticate_with_username(self,
                                    user_name,
                                    password,
                                    developer_token):
        '''
        Sets the authentication property of the global AuthorizationData instance with PasswordAuthentication.
        '''
        authentication = PasswordAuthentication(
            user_name=user_name, password=password)

        # Assign this authentication instance to the global authorization_data.
        self.authorization_data.developer_token = developer_token
        self.authorization_data.authentication = authentication

    def authenticate_with_oauth(self):
        '''
        Sets the authentication property of the global AuthorizationData
        instance with OAuthDesktopMobileAuthCodeGrant.

        Must be called after every client instantiation!!!
        '''
        # If you already have both an access token and refresh token,
        # then you can construct OAuthDesktopMobileAuthCodeGrant with OAuthTokens.
        authentication = OAuthWebAuthCodeGrant(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirection_uri='http://localhost',
            oauth_tokens=OAuthTokens(
                access_token=None,
                access_token_expires_in_seconds=0,
                refresh_token=self.refresh_token))

        # It is recommended that you specify a non guessable 'state' request parameter to help prevent
        # cross site request forgery (CSRF).
        authentication.state = self.CLIENT_STATE

        # Assign this authentication instance to the global authorization_data.
        self.authorization_data.authentication = authentication

        # Register the callback function to automatically save the refresh token anytime it is refreshed.
        # Uncomment this line if you want to store your refresh token. Be sure to save your refresh token securely.
        self.authorization_data.authentication.token_refreshed_callback = lambda x: self._save_refresh_token(x)

        try:
            # If we have a refresh token let's refresh it
            if self.refresh_token is not None:
                self.authorization_data.authentication.request_oauth_tokens_by_refresh_token(
                    self.refresh_token)
            else:
                # If using this not in kbc, call this method for interactive authorization
                # self._request_user_consent()
                raise AuthenticationError(
                    "For use in keboola you must supply a refresh token in the "
                    "configuration. For interactive use, call the"
                    "self._request_user_consent() method to trigger "
                    "the auth process"
                                          "")
        except OAuthTokenRequestException as e:
            # The user could not be authenticated or the grant is expired.
            # The user must first sign in and if needed grant the client application access to the requested scope.

            # If using this not in kbc, call this method for interactive authorization
            # self._request_user_consent()
            logging.error(e)
            raise AuthenticationError("Refresh token is invalid, or expired. Please reauthorize the application!")


    @property
    def refresh_token(self):
        return self._refresh_token

    def _save_refresh_token(self, oauth_tokens):
        '''
        Stores a refresh token locally. Be sure to save your refresh token securely.
        '''
        self._refresh_token = oauth_tokens.refresh_token

    def _request_user_consent(self):
        print(self.authorization_data.authentication.
              get_authorization_endpoint())
        # For Python 3.x use 'input' instead of 'raw_input'
        response_uri=input(
            "You need to provide consent for the application to access your Bing Ads accounts. " \
            "After you have granted consent in the web browser for the application to access your Bing Ads accounts, " \
            "please enter the response URI that includes the authorization 'code' parameter: \n"
        )

        if self.authorization_data.authentication.state != self.CLIENT_STATE:
            raise Exception(
                "The OAuth response state does not match the client request state."
            )

        # Request access and refresh tokens using the URI that you provided manually during program execution.
        self.authorization_data.authentication.request_oauth_tokens_by_response_uri(
            response_uri=response_uri)



class Client(AuthClient):
    # https://msdn.microsoft.com/en-us/library/bing-ads-reporting-reporttimeperiod.aspx
    predefined_times = [
        "Today", "Yesterday", "LastSevenDays", "ThisWeek", "LastWeek",
        "LastFourWeeks", "ThisMonth", "LastMonth", "LastThreeMonths",
        "LastSixMonths", "ThisYear", "LastYear"
    ]

    ad_perf_report_fname = 'AdPerformance.csv'
    # from here
    # https://msdn.microsoft.com/en-us/library/bing-ads-reporting-adperformancereportcolumn.aspx
    ad_perf_report_columns = [
        "TimePeriod", "AccountName", "AccountNumber", "AccountId",
        "CampaignName", "CampaignId", "AdGroupName", "AdId",
        "AdGroupId", "AdTitle", "AdDescription",
        "AdType", "CurrencyCode", "AdDistribution", "Impressions",
        "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition",
        "Conversions", "ConversionRate", "CostPerConversion",
        "DestinationUrl", "DeviceType", "Language", "DisplayUrl",
        "BusinessListingId", "BusinessListingName", "BusinessCategoryId",
        "BusinessCategoryName", "AdStatus", "Network", "TopVsOther",
        "BidMatchType", "DeliveredMatchType", "DeviceOS", "Assists",
        "Revenue", "ReturnOnAdSpend", "CostPerAssist", "RevenuePerConversion",
        "RevenuePerAssist", "TrackingTemplate", "CustomParameters",
        "FinalURL", "FinalMobileURL", "FinalAppURL", "AccountStatus",
        "CampaignStatus", "AdGroupStatus", "TitlePart1", "TitlePart2",
        "Path1", "Path2"]



    def __init__(self, *auth_args, **auth_kwargs):
        """

        This client implements the actual methods to communicate with the API

        Args:
            developer_token: got from bingads registration
            client_id (str): got during app registration
            client_secret (str): secret for oauth2
            refresh_token: If you have one, otherwise you will be prompted for
                consent
            customer_id:  get from bingads ui
            account_id:  get from bingads ui
            environment: 'production' or 'sandbox'
            _username: sandbox username
            _password: sandbox password
            _devkey: sandbox developer_key

        """
        super().__init__(*auth_args, **auth_kwargs)

        self.performance_report_fname = 'performance_report_{account_id}.csv'
        self.timeout_ms = 20 * 60 * 1000  # 20 minutes - is that enough??
        if self._environment == 'production':
            self.authenticate_with_oauth()
        elif self._environment == 'sandbox':
            self._authenticate_with_username(
                user_name=self._username,
                password=self._password,
                developer_token=self._devkey
            )
        else:
            raise ValueError("Unknown environment!")

        self.reporting_service = ServiceClient(
            service='ReportingService',
            authorization_data=self.authorization_data,
            version=11)

        self.reporting_service_manager = ReportingServiceManager(
            self.authorization_data,
            poll_interval_in_milliseconds=5000,
            environment=self._environment)

        # self.bulk_service_manager = BulkServiceManager(
        #     authorization_data=self.authorization_data,
        #     poll_interval_in_milliseconds=5000,
        #     environment=self._environment, )

        # self.campaign_service = ServiceClient(
        #     service='CampaignManagementService',
        #     authorization_data=self.authorization_data,
        #     environment=self._environment,
        #     version=11, )

        # self.customer_service = ServiceClient(
        #     'CustomerManagementService',
        #     authorization_data=self.authorization_data,
        #     environment=self._environment,
        #     version=11, )

    def _custom_date_range(self, day, month, year):
        custom_date_range = self.reporting_service.factory.create('Date')
        custom_date_range.Day = day
        custom_date_range.Month = month
        custom_date_range.Year = year
        return custom_date_range

    def _get_ad_performance_report_request(
            self,
            predefined_time=None,
            complete_data=False,
            start_date=None,
            end_date=None,
            columns=None,
            aggregation='Daily',
            report_name='AdPerformance'):
        '''
        Build a keyword performance report request, including Format, ReportName, Aggregation,
        Scope, Time, Filter, and Columns.

        '''

        logging.info("Building AdPerformance report request")
        report_request = self.reporting_service.factory.create('AdPerformanceReportRequest')
        report_request.Format = 'Csv'
        report_request.ReportName = report_name
        report_request.ReturnOnlyCompleteData = complete_data
        report_request.Aggregation = aggregation
        report_request.Language = 'English'
        report_request.ExcludeReportFooter = True
        report_request.ExcludeReportHeader = True

        scope = self.reporting_service.factory.create(
            'AccountThroughAdGroupReportScope')
        scope.AccountIds = {'long': self.account_id}
        scope.Campaigns = None
        scope.AdGroups = None
 
        report_request.Scope = scope

        report_time = self.reporting_service.factory.create('ReportTime')
        # You may either use a custom date range or predefined time.

        # can supply either predefined time or start/end date
        # if both are defined, the predefined time has priority over custom
        if predefined_time is not None:
            if predefined_time in self.predefined_times:
                logging.info(
                    "Building report with predefinedTime %s", predefined_time)
                report_time.PredefinedTime = predefined_time
            else:
                raise ValueError("predefined_time must be one of '{}'\n"
                                 "not '{}'".format(self.predefined_times,
                                                   predefined_time))
        else:
            yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=0)).date()
            if start_date:
                start_dt = self._clean_date(start_date)
                logging.info(
                    "Building report with startTime %s", start_dt)
                custom_date_range_start = self._custom_date_range(
                    start_dt.day, start_dt.month, start_dt.year)
                report_time.CustomDateRangeStart = custom_date_range_start
            else:
                raise ValueError(
                    "report start_date is not defined,"
                    "use format %d-%m-%Y, or define `predefined_time`")

            if end_date:
                end_dt = self._clean_date(end_date)
                logging.info(
                    "Building report with endTime %s", end_dt)
                custom_date_range_end = self._custom_date_range(
                    end_dt.day, end_dt.month, end_dt.year)
            else:
                custom_date_range_end = self._custom_date_range(
                    yesterday.day, yesterday.month, yesterday.year)
                # Default to yesterday
                logging.info(
                    "Building report with endTime %s (yesterday),"
                    " because endTime parameter is not set.", yesterday)
                report_time.CustomDateRangeEnd = custom_date_range_end

        report_request.Time = report_time

        report_columns = self.reporting_service.factory.create(
            'ArrayOfAdPerformanceReportColumn')
        # available columns here

        report_columns.AdPerformanceReportColumn.append(columns or self.ad_perf_report_columns)

        report_request.Columns = report_columns

        return report_request

    @log_soap_errors
    def download_ad_performance_report(self,
                                       outdir='/tmp/exbingads_reports',
                                       report_filename=None,
                                       startDate=None,
                                       endDate=None,
                                       predefinedTime=None,
                                       completeData=True,
                                       columns=None,
                                       aggregation='Daily'):
        """Send a request for downloading the report, wait for completition

        Also create a manifest for uploading to storage
        """
        report_filename = report_filename or self.ad_perf_report_fname
        start_date = startDate
        end_date = endDate
        predefined_time = predefinedTime
        complete_data = completeData
        try:
            os.makedirs(outdir)
        except FileExistsError:
            logging.debug("outdir %s already exists", outdir)
            pass
        logging.info("Downloading performance report for account_id %s",
                     self.account_id)
        report_request = self._get_ad_performance_report_request(
            predefined_time=predefined_time,
            start_date=start_date,
            end_date=end_date,
            complete_data=complete_data,
            aggregation=aggregation)

        reporting_download_parameters = ReportingDownloadParameters(
            report_request=report_request,
            result_file_directory=outdir,
            result_file_name=report_filename,
            overwrite_result_file=True,
            timeout_in_milliseconds=self.timeout_ms)

        logging.info("Initiating download")
        outpath = self.reporting_service_manager.download_file(
            reporting_download_parameters)
        if outpath is not None:
            logging.info("No data was downloaded, perhaps no campaigns are running?")
        else:
            logging.info("Report downloaded to %s", outpath)
        return outpath

    def _clean_date(self, dt):
        if isinstance(dt, str):
            start_dt = datetime.strptime(dt, '%d-%m-%Y').date()
        elif isinstance(dt, (datetime.datetime, datetime.date)):
            start_dt = dt
        else:
            raise ValueError("datetime parameter must be"
                             " str in %d-%m-%Y format, or datetime object"
                             " not %s", dt)

        return start_dt
