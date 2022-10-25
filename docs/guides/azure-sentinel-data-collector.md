### Prepare your environment:

- [Install py42 into your Python environment](https://py42docs.code42.com/en/stable/userguides/gettingstarted.html#installation)
- [Create a Code42 API Client](https://support.code42.com/Incydr/Admin/Code42_console_reference/API_clients) to authenticate py42. The `Alerts Read` permission is required to query alerts.
- Gather your Azure Log Analytics `Workspace ID` and either `Primary Key` or `Secondary Key` to authenticate requests pushing data into Sentinel.

<aside style="margin: 30px">
<p style="margin-left: 30px">
<b>NOTE:</b> Workspace ID and Keys can be found in your Log Analytics Workspace Settings under <b>Agents Management</b> > <b>Log Analytics agent instructions</b>.
</aside>

### Writing the script:

First, import the py42 SDK client and required classes for building your Alert query:

```python
import py42.sdk
from py42.sdk.queries.alerts.alert_query import AlertQuery
from py42.sdk.queries.alerts.filters import DateObserved
```

Then construct your query. This example will search for Alerts created within the past 3 days. See
[py42 documentation](https://py42docs.code42.com/en/stable/userguides/searches.html#search-alerts) for details on how
to customize your own query.

```python
from datetime import datetime, timedelta

date_filter = DateObserved.on_or_after(datetime.utcnow() - timedelta(days=3))
alert_query = AlertQuery(date_filter)
```

<aside style="margin: 30px">
<p style="margin-left: 30px">
<b>NOTE:</b> If you are scheduling this script to run regularly, you'll want to store the last retrieved alert's
timestamp to use as the starting point for the next query, so you don't ingest duplicate alerts.
</aside>

Initialize the py42 SDK object with your API client details:

```python
sdk = py42.sdk.from_api_client(
    host_address="https://console.us.code42.com",
    client_id="<your_client_id>",
    client_secret="<your_secret>"
)
```

Fetch the alerts with your query:

```python
response = sdk.alerts.search(query)
```

<aside style="margin: 30px">
<p style="margin-left: 30px">
<b>NOTE:</b> If you anticipate needing to ingest a large number of alerts, you may want to use the
<a href=https://py42docs.code42.com/en/stable/methoddocs/alerts.html#py42.clients.alerts.AlertsClient.search_all_pages>search_all_pages()</a>
method, which will yield a generator of pages that you can iterate over to get all the results in a single call.
</aside>

The Sentinel HTTP endpoint accepts a list of JSON objects in the request body, to prepare the py42 response for sending
to Sentinel, you just need to extract the `alerts` data from the py42 response and convert it to a JSON string:

```python
import json

response = sdk.alerts.search(query)
body = json.dumps(response.data["alerts"])
```

Then we can use the [Python example](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api#python-sample)
from the Data Collector API documentation to authenticate and send the Incydr Alerts to Sentinel. The example is
recreated here with the py42 code replacing the example data:

```python
import json
import requests
import datetime
import hashlib
import hmac
import base64

import py42.sdk
from py42.sdk.queries.alerts.alert_query import AlertQuery
from py42.sdk.queries.alerts.filters import DateObserved

# Update the customer ID to your Log Analytics workspace ID
customer_id = 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

# For the shared key, use either the primary or the secondary Connected Sources client authentication key
shared_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# This creates a new Custom Log type for Incydr Alerts
log_type = 'IncydrAlert'


#####################
##Incydr Alert Query#
#####################

date_filter = DateObserved.on_or_after(datetime.datetime.utcnow() - datetime.timedelta(days=3))
alert_query = AlertQuery(date_filter)

sdk = py42.sdk.from_api_client(
    host_address="https://console.us.code42.com",
    client_id="<your_client_id>",
    client_secret="<your_secret>"
)
response = sdk.alerts.search(query)
body = json.dumps(response.data["alerts"])

#####################
##Sentinel Functions#
#####################

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print("Response code: {}".format(response.status_code))

post_data(customer_id, shared_key, body, log_type)
```

After the script is run, you should be able to query the `IncydrAlert_CL` log table and see the Incydr Alert data.
