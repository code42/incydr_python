# Migration

---

Documentation on notable changes from the original Code42CLI tool.

## Authentication

Authentication was previously done by specifying credentials upon profile creation.  Credentials could either be a username/password for an individual Code42 user, or the key/secret for an API client.

Authentication is now done exclusively through environment variables and must be for an API Client.  More details on setting up [Incydr CLI Authentication](index.md#Authentication).

### Profiles

All settings are configured via environment variables.  Individual profiles are no longer available.

Stored checkpoints are associated with the API Client ID used for authentication during the command execution.

## Unsupported Functionality

Several commands and other functionality included in the original Code42 CLI is no longer supported in the Incydr CLI.

The Incydr CLI is focused exclusively on security-related functionality and only supports actions that correspond with our publicly documented APIs on the [Developer Portal](https://developer.code42.com/).
Commands that were previously supported in the original Code42 CLI but are no longer present in the Incydr CLI may have been preservation-related, or they may have leveraged internal and/or deprecated APIs.

### Commands

The commands listed below are unavailable in the Incydr CLI and do not currently have a replacement.

* `devices activate`
* `devices deactivate`
* `devices list-backup-sets`
* `devices rename`
* `orgs show`
* `orgs list`
* `alert-rules add-user`
* `alert-rules remove-user`
* all `legal-hold` commands

### Other Changes

* Backup data is not included in `devices list` and `devices show`.
* `send-to` commands are not available.  Server logging is now done with the `--output PROTOCOL:HOSTNAME:PORT` option on the `alerts search`, `audit-log search`, and `file-event search` commands.
* `departing-employee`, `high-risk-employee`, and `detection-lists` commands have been deprecated in the original CLI and not available.
* The V1 file event data model is no longer supported. The Incydr CLI uses the latest V2 file event data model.  Previously, you had to opt into this by enabling the `use-v2-file-events` profile setting in the Code42 CLI.
* User token authentication via a username and password is no longer supported.  API clients should be used for authentication.
* File event checkpointing now stores the original query it was run with and subsequent runs with the same checkpoint will ignore any additional filters.  All queries require a `--start` value as fallback for the `checkpoint`.
