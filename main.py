"""
Config:
{
    "#devKey": "yourdevkey",
    "customerId": 123456,
    "accountId": 123456,
    "bucket": "in.c-test",
    "incremental": false,
    "sinceLast" : false,
    "completeData": true # optional, default to true
    "reportRequests": [
      {
        "type": "AdsPerformance",
        "predefinedTime": 'lastSevenDays' # atm this only works, not custom ranges
        "columns": [],
        "pk_columns": []}

      },
    ]
  }

"""
import resource
import traceback
import sys
import os
from exbingads.extractor import main
from exbingads.utils import ExtractorError, AuthenticationError
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        main(os.getenv("KBC_DATADIR"))
    except (ValueError, ExtractorError, AuthenticationError) as e:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)
    finally:
        logging.info("max memory usage %s bytes/kilobytes?", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
