"""
The interface
"""
import resource
import traceback
import sys
import os
from exbingads.extractor import main
from exbingads.utils import ExtractorError, AuthenticationError
from bingads.exceptions import OAuthTokenRequestException
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        main(os.getenv("KBC_DATADIR"))
    except (ValueError, ExtractorError, OAuthTokenRequestException, AuthenticationError) as e:
        logging.error(e)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)
    finally:
        logging.info("max memory usage %s kilobytes?", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
