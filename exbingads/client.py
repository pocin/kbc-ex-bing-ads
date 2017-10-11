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
from exbingads.utils import log_soap_errors

import logging


class AuthClient:
    # It is recommended that you specify a non guessable 'state' request parameter to help prevent
    # cross site request forgery (CSRF).

    def __init__(self,
                 developer_token,
                 client_id,
                 refresh_token=None,
                 customer_id=None,
                 account_id=None,
                 authentication=None,
                 environment='production'):
        """
        Authenticate a client and prepare "Services" for calling the api


        Args:
            developer_token: get from https://developers.bingads.microsoft.com/Account
            client_id: the registered app id from MS https://apps.dev.microsoft.com/#/application/
            refresh_token: (optional) if you have one, otherwise the next step will trigger OAuth webbrowser flow
            customer_id: # https://bingads.microsoft.com/cc/accounts
            account_id: # https://bingads.microsoft.com/cc/accounts
            authentication: leave blank probably?

        Usage
            >>> client = AuthClient(**kwargs)
            >>> #will either prompt you for uri or succeede if refresh_token was supplied
            >>> client.authenticate_with_oauth()
            >>> # actually use the client
            >>> client.bulk_service_manager....

        """
        self._refresh_token = refresh_token
        self._environment = environment
        self.client_id = client_id
        self.account_id = account_id
        self.customer_id = customer_id
        self.CLIENT_STATE = md5(str(datetime.datetime.now()).encode(
            'utf-8')).hexdigest()

        self.authorization_data = AuthorizationData(
            account_id=account_id,
            customer_id=customer_id,
            developer_token=developer_token,
            authentication=authentication)

    def _authenticate_with_username(self,
                                    user_name="UserNameGoesHere",
                                    password="PasswordGoesHere"):
        '''
        Sets the authentication property of the global AuthorizationData instance with PasswordAuthentication.
        '''
        authentication = PasswordAuthentication(
            user_name=user_name, password=password)

        # Assign this authentication instance to the global authorization_data.
        self.authorization_data.authentication = authentication

    def authenticate_with_oauth(self):
        '''
        Sets the authentication property of the global AuthorizationData
        instance with OAuthDesktopMobileAuthCodeGrant.

        Must be called after every client instantiation!!!
        '''
        # If you already have both an access token and refresh token,
        # then you can construct OAuthDesktopMobileAuthCodeGrant with OAuthTokens.
        authentication = OAuthDesktopMobileAuthCodeGrant(
            client_id=self.client_id,
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
                self._request_user_consent()
        except OAuthTokenRequestException:
            # The user could not be authenticated or the grant is expired.
            # The user must first sign in and if needed grant the client application access to the requested scope.
            self._request_user_consent()


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


            else:
                output_bing_ads_webfault_error(api_errors)
        elif hasattr(ex.fault, 'detail') \
            and hasattr(ex.fault.detail, 'EditorialApiFaultDetail') \
            and hasattr(ex.fault.detail.EditorialApiFaultDetail, 'OperationErrors') \
            and hasattr(ex.fault.detail.EditorialApiFaultDetail.OperationErrors, 'OperationError'):
            api_errors=ex.fault.detail.EditorialApiFaultDetail.OperationErrors.OperationError
            if type(api_errors) == list:
                for api_error in api_errors:
                    output_bing_ads_webfault_error(api_error)
            else:
                output_bing_ads_webfault_error(api_errors)
                # Handle serialization errors e.g. The formatter threw an exception while trying to deserialize the message: 
                # There was an error while trying to deserialize parameter https://bingads.microsoft.com/CampaignManagement/v10:Entities.
        elif hasattr(ex.fault, 'detail') \
            and hasattr(ex.fault.detail, 'ExceptionDetail'):
            api_errors=ex.fault.detail.ExceptionDetail
            if type(api_errors) == list:
                for api_error in api_errors:
                    logging.error(api_error.Message)
            else:
                logging.error(api_errors.Message)
        else:
            raise Exception('Unknown WebFault')

    def _output_bulk_campaigns(self, bulk_entities):
        for entity in bulk_entities:
            logging.error("BulkCampaign: \n")
            logging.error("Campaign Name: {0}".format(entity.campaign.Name))
            logging.error("Campaign Id: {0}".format(entity.campaign.Id))

            if entity.has_errors:
                output_bulk_errors(entity.errors)

            logging.error('')

    def _output_bulk_errors(self, errors):
        for error in errors:
            if error.error is not None:
                logging.error("Number: {0}".format(error.error))
                logging.error("Error: {0}".format(error.number))
            if error.editorial_reason_code is not None:
                logging.error("EditorialTerm: {0}".format(error.editorial_term))
                logging.error("EditorialReasonCode: {0}".format(error.editorial_reason_code))
                logging.error("EditorialLocation: {0}".format(error.editorial_location))
                logging.error("PublisherCountries: {0}".format(error.publisher_countries))
                logging.error('')


