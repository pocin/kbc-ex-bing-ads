# About
A V11 bing ads api extractor for Keboola Connection
API V10 is deprecated on 31.10.2017
See [this](https://msdn.microsoft.com/en-us/library/bing-ads-api-migration-guide(v=msads.100).aspx#Reporting) for breaking changes. Most notably, there are some differences in column nomenclature

At this moment, this extractor 
- supports downloading AdsPerformance reports using  
  - custom date ranges
  - predefinedTimes (recommended as it creates an overlapping window, ideal for incremental loads)

## Config
### Predefined time (Recommended)
Here is a sample config (this one should work)

This config will 
- download `AdPerformance` report for given customer/accountId. You can select up to 1000 accountIds, so you dont have to create an extractor config for each account.
- Save output to `in.c-ex-bingads-v11.AdPerformance`
- The time period will be `LastSevenDays` (for a complete list of `predefinedTimes` see [this](https://msdn.microsoft.com/en-us/library/bing-ads-reporting-reporttimeperiod.aspx)).
- The table will be loaded incrementally, for this to work properly, don't forget to set `pkey` parameter which defines primary key columns. In this case, the pkey should be sufficient for correct incremental loading
- It will download all possible columns (`columns` parameter is `[]`) for this report. See [this](https://msdn.microsoft.com/en-us/library/bing-ads-reporting-adperformancereportcolumn.aspx) if you want just a subset. (**Caveat** - a column name `TimePeriod` denotes the timestamp, but is named `GregorianDate` in the final report!)
- aggregate the results by day [see possible values](https://msdn.microsoft.com/en-us/library/bing-ads-reporting-nonhourlyreportaggregation.aspx). See [this](https://msdn.microsoft.com/en-US/library/bing-ads-get-reports-guide.aspx#Aggregation_Time) to check whether given aggregation level is compatible with the specified `predefinedTime`.


```
{
    "#devKey": "1234cbas",
    "customerId": 12345,
    "accountId": [1234566], # always an array
    "bucket": "in.c-ex-bingads-v11",
    "completeData": false,
    "incremental": true,
    "reportRequests": [
        {
            "type": "AdsPerformance",
            "predefinedTime": "LastSevenDays",
            "aggregation": "Daily",
            "columns": [],
            "pkey": [
                "AccountId", "GregorianDate", "CampaignId", "AdId",
                "AdGroupId", "AdType", "Device_type", "Language", "Network",
                "TopVsOther", "BiddedMatchType", "MatchType", "DeviceOS"
                ]
        }
    ]
}
}
```

### Using custom ranges


```
{
    "#devKey": "1234cbas",
    "customerId": 12345,
    "accountId": [1234566], # always an array
    "bucket": "in.c-ex-bingads-v11",
    "completeData": false,
    "incremental": true,
    "reportRequests": [
        {
            "type": "AdsPerformance",
            "startDate": "23-06-2017", #dd-mm-yyyy format, if you omit endDate parameter, 'today' is used
            "aggregation": "Daily",
            "columns": [], #leave blank for all columns
            "pkey": [
                "AccountId", "GregorianDate", "CampaignId", "AdId",
                "AdGroupId", "AdType", "Device_type", "Language", "Network",
                "TopVsOther", "BiddedMatchType", "MatchType", "DeviceOS"
                ]
        }
    ]
}
}
```

# Developer info (safe to ignore for end users)

Get bingads user info here https://developers.bingads.microsoft.com/Account
Get a dev token here https://developers.bingads.microsoft.com/Account
Register an app here (clientId) https://apps.dev.microsoft.com/#/application/ (choose native app)

Use this to get OAuth tokens (Authorization code grant flow) https://msdn.microsoft.com/en-us/library/bing-ads-user-authentication-oauth-guide.aspx#registerapplication

Here is a big python code sample https://msdn.microsoft.com/en-us/library/bing-ads-python-walkthrough-desktop-application(v=msads.100).aspx

