# Automate and integrate with Incydr

Welcome to the Code42 Developer Portal! Here you will find resources to assist you in leveraging the Code42 platform for automation and scripting. Code42 offers a powerful set of tools you can use for everything from performing automated actions to integrating with your company's security applications.

We offer several different approaches to integrate into Code42 so you can choose the right level of control mixed with your desired simplicity to integrate into our product. Choose the right level of control mixed with your complexity needs.

| Tool  | Interface | Primary use | Flexibility | Development Time |
| ----- | --------- | ----------- | ------------| ---------------- |
| [Code42 REST API](#rest-api) | language/http client of your choice | Fully customized solution | Most | Moderate |
| [Py42](#py42) | Python library | Custom scripting | Moderate | Moderate
| [Code42 CLI](#code42-command-line-interface) | Command Line | Prebuilt, out-of-the-box scripts | Least | Least



## REST API

The Code42 REST API is available for a wide variety of use cases, from performing automated actions to integrating with existing systems. The Code42 API is accessible through many tools, such as web browsers, scripting tools, and programming languages.

### Example Use Cases

* Directly having another tool provision or de-provision users
* Complex workflow applications where Python isn't available
* Applications where direct control over options is a necessity

Code42 API access is included with any licensed subscription of a Code42 product. See our [reference documentation](/api/) for the complete schema and methods available.

## Py42

py42 is an [open source](https://github.com/code42/py42) Python SDK wrapper around the Code42 API that also provides several utility methods. py42 helps accelerate development of internal applications using the Code42 platform, while avoiding the overhead of session or authentication management, paging, and JSON parsing.

### Example Use Cases

* [Search file events](https://py42docs.code42.com/en/stable/userguides/searches.html)
* Manage users on the [Departing Employee](https://py42docs.code42.com/en/stable/userguides/departingemployee.html) or [High Risk](https://py42docs.code42.com/en/stable/userguides/highriskemployee.html) lists
* Manage [device](https://py42docs.code42.com/en/stable/userguides/devicesettings.html) or [organization](https://py42docs.code42.com/en/stable/userguides/orgsettings.html) settings

For more information, see the full [py42 documentation](https://py42docs.code42.com).


## Code42 Command-line Interface

The Code42 command-line interface (CLI) offers a way to interact with your Code42 environment without using the Code42 console or making API calls directly. If you have familiarity with command line tools, Code42, and have Python and PyPI (pip) installed, you can get started quickly and easily with the Code42 CLI.

### Example Use Cases

* [Automate managing users on the Departing Employee and High Risk lists](https://clidocs.code42.com/en/latest/userguides/detectionlists.html)
* [Automate legal hold user management](https://clidocs.code42.com/en/latest/userguides/legalhold.html)
* [Extract events from Code42, and optionally send them to a syslog server or SIEM](https://clidocs.code42.com/en/latest/userguides/siemexample.html)

Setting the CLI to run as a scheduled task in Windows or added to the crontab in Linux can quickly get automations up and running. We welcome submissions of code as well as ideas to our [GitHub repository](https://github.com/code42/code42cli) to be considered for a future update.

For more information, see the full [Code42 CLI documentation](https://clidocs.code42.com).
