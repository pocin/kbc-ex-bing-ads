from keboola import docker
import logging
from suds import WebFault
from functools import wraps

REQUIRED_PARAMS = ['accountId', 'customerId', '#devKey', 'bucket']


def parse_config(datadir):
    cfg = docker.Config(datadir)
    params = cfg.get_parameters()
    for p in REQUIRED_PARAMS:
        if p not in params:
            raise ValueError("config parameter '{}' must be defined".format(p))
    return params


def output_bing_ads_webfault_error(error):
    if hasattr(error, 'ErrorCode'):
        logging.error("ErrorCode: {0}".format(error.ErrorCode))
    if hasattr(error, 'Code'):
        logging.error("Code: {0}".format(error.Code))
    if hasattr(error, 'Message'):
        logging.error("Message: {0}".format(error.Message))
        logging.error('')


def output_webfault_errors(ex):
    if hasattr(ex.fault, 'detail') \
    and hasattr(ex.fault.detail, 'ApiFault') \
    and hasattr(ex.fault.detail.ApiFault, 'OperationErrors') \
    and hasattr(ex.fault.detail.ApiFault.OperationErrors, 'OperationError'):
        api_errors = ex.fault.detail.ApiFault.OperationErrors.OperationError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'AdApiFaultDetail') \
        and hasattr(ex.fault.detail.AdApiFaultDetail, 'Errors') \
        and hasattr(ex.fault.detail.AdApiFaultDetail.Errors, 'AdApiError'):
        api_errors = ex.fault.detail.AdApiFaultDetail.Errors.AdApiError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'ApiFaultDetail') \
        and hasattr(ex.fault.detail.ApiFaultDetail, 'BatchErrors') \
        and hasattr(ex.fault.detail.ApiFaultDetail.BatchErrors, 'BatchError'):
        api_errors = ex.fault.detail.ApiFaultDetail.BatchErrors.BatchError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'ApiFaultDetail') \
        and hasattr(ex.fault.detail.ApiFaultDetail, 'OperationErrors') \
        and hasattr(ex.fault.detail.ApiFaultDetail.OperationErrors, 'OperationError'):
        api_errors = ex.fault.detail.ApiFaultDetail.OperationErrors.OperationError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'EditorialApiFaultDetail') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail, 'BatchErrors') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail.BatchErrors, 'BatchError'):
        api_errors = ex.fault.detail.EditorialApiFaultDetail.BatchErrors.BatchError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'EditorialApiFaultDetail') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail, 'EditorialErrors') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail.EditorialErrors, 'EditorialError'):
        api_errors = ex.fault.detail.EditorialApiFaultDetail.EditorialErrors.EditorialError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'EditorialApiFaultDetail') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail, 'OperationErrors') \
        and hasattr(ex.fault.detail.EditorialApiFaultDetail.OperationErrors, 'OperationError'):
        api_errors = ex.fault.detail.EditorialApiFaultDetail.OperationErrors.OperationError
        if type(api_errors) == list:
            for api_error in api_errors:
                output_bing_ads_webfault_error(api_error)
        else:
            output_bing_ads_webfault_error(api_errors)
            # Handle serialization errors e.g. The formatter threw an exception while trying to deserialize the message:
            # There was an error while trying to deserialize parameter https://bingads.microsoft.com/CampaignManagement/v10:Entities.
    elif hasattr(ex.fault, 'detail') \
        and hasattr(ex.fault.detail, 'ExceptionDetail'):
        api_errors = ex.fault.detail.ExceptionDetail
        if type(api_errors) == list:
            for api_error in api_errors:
                logging.error(api_error.Message)
        else:
            logging.error(api_errors.Message)
    else:
        raise Exception('Unknown WebFault')


def output_bulk_campaigns(bulk_entities):
    for entity in bulk_entities:
        logging.error("BulkCampaign: \n")
        logging.error("Campaign Name: {0}".format(entity.campaign.Name))
        logging.error("Campaign Id: {0}".format(entity.campaign.Id))

        if entity.has_errors:
            output_bulk_errors(entity.errors)

        logging.error('')


def output_bulk_errors(errors):
    for error in errors:
        if error.error is not None:
            logging.error("Number: {0}".format(error.error))
            logging.error("Error: {0}".format(error.number))
        if error.editorial_reason_code is not None:
            logging.error("EditorialTerm: {0}".format(error.editorial_term))
            logging.error("EditorialReasonCode: {0}".format(
                error.editorial_reason_code))
            logging.error("EditorialLocation: {0}".format(
                error.editorial_location))
            logging.error("PublisherCountries: {0}".format(
                error.publisher_countries))
            logging.error('')

def log_soap_errors(f):
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except WebFault as ex:
            output_webfault_errors(ex)
            raise
        except Exception as ex:
            logging.error(ex)
            raise
    return wrapped
