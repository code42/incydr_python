# Automate and integrate with Incydr

Welcome to the Code42 Developer Portal! Here you will find resources to assist you in leveraging the Code42 platform for automation and scripting. Code42 offers a powerful set of tools you can use for everything from performing automated actions to integrating with your company's security applications.

We offer several different approaches to integrate into Code42 so you can choose the right level of control mixed with your desired simplicity to integrate into our product.

| Tool  | Interface | Primary use | Flexibility | Development Time |
| ----- | --------- | ----------- | ------------| ---------------- |
| [Code42 REST API](#rest-api) | language/http client of your choice | Fully customized solution | Most | Moderate |
| [Incydr SDK - Python](sdk/index.md) | Python library | Custom scripting | Moderate | Moderate
| [Incydr SDK - CLI](cli/index.md) | Command Line | Prebuilt, out-of-the-box scripts | Least | Least


## REST API

The Code42 REST API is available for a wide variety of use cases, from performing automated actions to integrating with existing systems. The Code42 API is accessible through many tools, such as web browsers, scripting tools, and programming languages.

### Example Use Cases

* Directly having another tool provision or de-provision users
* Complex workflow applications where Python isn't available
* Applications where direct control over options is a necessity

Code42 API access is included with any licensed subscription of a Code42 product. See our [reference documentation](api/) for the complete schema and methods available.

## Incydr SDK

The Incydr SDK is a Python wrapper around the public Code42 APIs with some additional utility.

The SDK contains a [Python client](#python-sdk) and a [CLI tool extension](#cli-tool) to accelerate development of internal applications using the Incydr platform,
while avoiding the overhead of session or authentication management, paging, and JSON parsing.

We welcome submissions of code as well as ideas to our open source [GitHub repository](https://github.com/code42/incydr_python) to be considered for a future update.

### Python SDK

The Incydr SDK provides a Python client for interacting with the [Code42 Incydr API](api/).

#### Example Use Cases

* [Search file events](sdk/clients/file_event_queries.md)
* Manage [watchlist](sdk/clients/watchlists.md) membership
* Manage [users](sdk/clients/users.md) and [user risk profiles](sdk/clients/user_risk_profiles.md)

For more information, see the full [Incydr Python SDK Documentation](sdk/index.md).

### CLI Tool

The Incydr SDK CLI tool is an extension of the Python SDK and offers a way to interact with your Code42 environment without using the Code42 console or making API calls directly.
If you have familiarity with command line tools, Code42, and have Python and PyPI (pip) installed, you can get started quickly and easily with the Incydr SDK CLI.

#### Example Use Cases

* [Automate watchlist membership](cli/cmds/watchlists.md)
* [Automate user management](cli/cmds/users.md)
* [Extract events from Code42, and optionally send them to a syslog server or SIEM](cli/syslogging.md)

Setting the CLI to run as a scheduled task in Windows or added to the crontab in Linux can quickly get automations up and running.

For more information, see the full [Incydr CLI tool documentation](cli/index.md).

## Preservation Tools

!!! note
    The following resources provide preservation capabilities unavailable in the Incydr SDK. They will no longer be updated with the latest security functionality. Use the Incydr SDK for all security-related use cases.

### Py42

Py42 is an [open source](https://github.com/code42/py42) Python SDK wrapper around the Code42 API that also provides several utility methods.

For more information, see the full [py42 documentation](https://py42docs.code42.com).

### Code42 Command-line Interface

The Code42 command-line interface (CLI) offers a way to interact with your Code42 environment without using the Code42 console or making API calls directly.

For more information, see the full [Code42 CLI documentation](https://clidocs.code42.com).
