# Introduction

The Incydr CLI is a command line tool for interacting with the [Code42 Incydr API](https://developer.code42.com/api) created with [Click](https://click.palletsprojects.com/en/8.1.x/).
It's built on top of the [Incydr SDK](../sdk/index.md) Python client and the [Requests](https://requests.readthedocs.io/en/latest/) HTTP library.

## Installation

---

Install the CLI extension to the Incydr SDK with pip.  Use the following command:

```bash
$ pip install 'incydr[cli]'
```

See [Getting Started](getting_started.md) for more further details on setting up your Incydr CLI.

## Commands

---

The `incydr` command contains subcommand groups that map to each API action described in the
[Code42 API Reference](https://developer.code42.com/api). It offers a command for each API endpoint with options and arguments that
correspond to request parameters.

The following subcommand groups are available under the `incydr` command:

* [Alert Rules](alert_rules.md)
* [Alerts](alerts.md)
* [Audit Log](audit_log.md)
* [Cases](cases.md)
* [Departments](departments.md)
* [Devices](devices.md)
* [Directory Groups](directory_groups.md)
* [File Events](file_events.md)
* [Trusted Activities](trusted_activities.md)
* [Users & Risk Profiles](users.md)
* [Watchlists](watchlists.md)
