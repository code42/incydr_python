# Changelog

 All notable changes to this project will be documented in this file.

 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

 The intended audience of this file is for `incydr` SDK and CLI consumers -- as such, changes that don't affect
 how a consumer would use the library or CLI tool (e.g. adding unit tests, updating documentation, etc) are not captured
 here.

## 1.1.1 - 2023-06-02

### Fixed
- CLI `watchlists add|remove` commands for included and excluded users now batches requests to work around 100 user limit of backend API.

## 1.1.0 - 2023-05-01

### Added

- Better error messaging when authentication parameters or env vars missing when instantiating the `incydr.Client` or running CLI commands.
- Missing authentication parameters (`url`, `api_client_id`, or `api_client_secret`) causes client to raise new exception type: `AuthMissingError`.
- `incydr.exceptions` module has been added to the public API.
- Support for [Agents APIs](https://developer.code42.com/api/#tag/Agents), including:
  - An `agents.v1` client to the SDK with the following methods:
    - `client.agents.v1.get_page()` to query a single page of agents.
    - `client.agents.v1.iter_all()` to lazily iterate through all pages of agents.
    - `client.agents.v1.get_agent()` to retrieve details of a single agent by ID.
    - `client.agents.v1.update()` to update the `name` or `externalReference` field of an agent.
    - `client.agents.v1.activate()` to activate a list of agents by their IDs.
    - `client.agents.v1.deactivate()` to deactivate a list of agents by their IDs.
  - A set of `agents` CLI commands:
    - `incydr agents list` to list all agents in your environment (in table, CSV, or JSON formats).
    - `incydr agents show` to show the details of a given agent by ID.
    - `incydr agents bulk-activate` to activate a set of agents from CSV or JSON-LINES file input.
    - `incydr agents bulk-deactivate` to deactivate a set of agents from CSV or JSON-LINES file input.
- New search terms on the [incydr.enums.file_events.EventSearchTerm](https://developer.code42.com/sdk/enums/#event-search-terms) enum, enabling full support for querying the latest file event fields.
- New file event field models: `AcquiredFromGit`, `AcquiredFromSourceUser`, `UntrustedValues`.
- Various other additions to existing model fields.

## 1.0.1 - 2023-04-21

### Fixed

- Bug in the `user_risk_profile` client, where `get_page()` was using the incorrect query param for the page number.
- Bug in `AuditEventsPage` model that prevented some audit log events from being parsed correctly.
