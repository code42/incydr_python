# Changelog

 All notable changes to this project will be documented in this file.

 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

 The intended audience of this file is for `incydr` SDK and CLI consumers -- as such, changes that don't affect
 how a consumer would use the library or CLI tool (e.g. adding unit tests, updating documentation, etc) are not captured
 here.

## 1.3.0 (Unreleased)

### Added TODO

- Support for [Actors APIs](), including:
  - An `actors.v1` client to the SDK with the following methods:
    -
  - A set of `actors` CLI commands:
    -

## 1.2.0 - 2024-3-18

### Added

- The following agent health related fields will be present on the response when retrieving agents:
  - `serialNumber`
  - `machineId`
  - `agentHealthIssueTypes`
- Additional optional args in the SDK's agent client for filtering by agent health.
  - `client.agents.v1.get_page()` and `client.agents.v1.get_page()` now accept:
    - `agent_healthy: bool` - Retrieve only healthy agents with `True` or only unhealthy agents with `False`.  Defaults to returning all agents.
    - `agent_health_issue_types: List[str] | str`- Retrieve agents with any of the given health issues. Ex: `NOT_CONNECTING`
- Additional options in the CLI's agent command group for filtering by agent health:
  - `incydr agents list` now accepts:
    - `--healthy` - Retrieve only healthy agents.
    - `--unhealthy` - Retrieve only unhealthy agents.
    - Pass a comma separated list of health issue types to the unhealthy option to filter for agents with any of the given health issues. Ex: `--unhealthy NOT_CONNECTING,NOT_SENDING_SECURITY_EVENTS`
    - Use `incydr agents list --help` to see more specifics on the new command options.
- See the [SDK documentation](https://developer.code42.com/sdk/clients/agents/) and the [CLI documentation](https://developer.code42.com/cli/cmds/agents/#agents-list) for more details.

## 1.1.2 - 2023-12-11

### Fixed

- Saved search filter values can now accept a list of strings.  Prior to this fix this was incorrectly resulting in a model validation error.

## 1.1.1 - 2023-10-03

### Fixed

- Pinned Pydantic version to major version `1.*` following the release of Pydantic 2.0.

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
