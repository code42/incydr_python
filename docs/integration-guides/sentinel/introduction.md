Microsoft Sentinel can accept arbitrary json data as Custom Log sources, so you can ingest almost any type of Incydr
data for querying within Sentinel, including Alerts, File Events, and Audit Log events.

Sentinel has two methods of ingesting JSON data as Custom Log sources: the data collector HTTP API, and the Log
Analytics Linux agent. While the examples below will focus on Incydr Alerts, the patterns can be re-used for almost any
type of data you can pull from the Code42 API or CLI.

[Data collector API](azure-sentinel-data-collector.md)

[Log Analytics Agent](azure-sentinel-log-analytics.md)
