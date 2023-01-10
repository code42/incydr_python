# Migration

---

A brief documentation of notable changes from the original Code42CLI tool.

## Authentication

Authentication was previously done by specifying credentials upon profile creation.  Credentials could either be a username/password for an individual Code42 user, or the key/secret for an API client.

Authentication is now done exclusively through environment variables and must be for an API Client.  More details on setting up [Incydr CLI Authentication](index.md#Authentication).

### Profiles

All settings are configured via environment variables.  Individual profiles are no longer available.

## V2 Event Model

The Incydr CLI uses the latest file event data model.  Previously, you had to opt into this by enabling the `use-v2-file-events` profile setting.

### Checkpointing

File event checkpointing now stores the original query it was run with and subsequent runs with the same checkpoint will ignore any additional filters.  All queries require a `--start` value as fallback for the `checkpoint`.
