# Changelog

 All notable changes to this project will be documented in this file.

 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

 The intended audience of this file is for `incydr` SDK and CLI consumers -- as such, changes that don't affect
 how a consumer would use the library or CLI tool (e.g. adding unit tests, updating documentation, etc) are not captured
 here.

## Unreleased

### Updated

- CSV and JSON input for the CLI's bulk agent commands will now look for `agentGuid` as a column header, in addition to `agent_id`, `agentId`, and `guid`.

## 2.3.0 - 2025-03-18

### Added

- `watchlists.v2` methods are added to the SDK, for parity with the API.
- New CLI watchlist commands `list-excluded-actors` and `list-included-actors` to replace the deprecated `list-excluded-users` and `list-included-users`.

### Updated

- The CLI's `watchlists` commands now use the v2 watchlist API. These commands correctly use `actor_id` instead of `user_id`. While the previous user_id parameters will still work for now, we recommend that users switch as soon as possible to using actor_id instead.

### Fixed

- A bug where the api endpoint used to download audit log events was incorrect.

### Deprecated

- Devices methods in the SDK and CLI are deprecated. Use the Agents methods instead.
- Risk Profiles methods in the SDK and CLI, already deprecated, are more clearly marked.
- The SDK's `watchlists.v1` methods are deprecated.
- The CLI's watchlist group `list-excluded-users` and `list-included-users` commands are deprecated. Use `list-excluded-actors` and `list-included-actors` instead.

## 2.2.4 - 2025-03-11

### Added

- Improved documentation to clarify that all agent health issues can be queried and filtered using the CLI and SDK.

## 2.2.3 - 2025-02-05

### Fixed

- A bug where in some rare cases searching file events could cause the SDK to throw a validation error on the server's correct response.

## 2.2.2 - 2025-01-08

### Fixed

- A bug where dates (e.g. 2025-01-08) were incorrectly converted to timestamps when querying sessions.

## 2.2.1 - 2024-12-18

### Added

- Added support for python 3.13.

### Updated

- The CLI and SDK now have user-agent headers consistent with Code42 current standards.

### Removed

- Removed support for python 3.7 and 3.8, which are end-of-life.


## 2.2.0 - 2024-11-18

### Updated

- Updated the `FileEventV2` model to all existing fields at this time. For example, the recently added `responseControls` response object is now available on the model.
- Updated `EventQuery` objects to allow filtering by any string by removing the requirement that filter terms and values must match explicitly defined fields.  This allows end users to filter by fields recently added to the file event response without requiring an SDK update.
- `client.actors.v1.get_actor_by_name` now defaults to `prefer_parent=True`. Previously, it defaulted to `False`.

## 2.1.0 - 2024-09-30

### Added

- Support for the API to update actors.
  - `client.actors.v1.update_actor` - to update an actor's start date, end date, or notes.
- A CLI command to update an actor.
  - `incydr actors update` - to update an actor's start date, end date, or notes.

### Deprecated

- Risk Profiles methods and commands are now deprecated, replaced by the `actors` command group.

## 2.0.0 - 2024-05-10

### Added

- Support for the [Sessions APIs](https://developer.code42.com/api/#tag/Alerts-and-Sessions)
  - A `sessions.v1` client to the SDK with the following methods:
    - `client.sessions.v1.get_page()` - to query a page of sessions.
    - `client.sessions.v1.iter_all()` - to lazily iterate through all pages of sessions.
    - `client.sessions.v1.get_session_details()` - to retrieve the details of a single session specified by ID.
    - `client.sessions.v1.get_session_events()` - to retrieve the file events associated with a session specified by ID.
    - `client.sessions.v1.update_state_by_id()` - to update the state of a session specified by ID.
    - `client.sessions.v1.update_state_by_criteria()` - to update the state of all sessions matching the filter criteria.
    - `client.sessions.v1.add_note()` - to attach a note to a session specified by ID.
  - A set of `sessions` CLI commands:
    - `incydr sessions search` to search sessions by criteria. Includes various filter, output, and checkpointing options.
    - `incydr sessions show` to show session details.
    - `incydr sessions show-events` to show file events associated with the session.
    - `incydr sessions update` to update the state and/or note of a session.
    - `incydr sessions bulk-update-state` to update the state and attach an optional note to multiple sessions at once
- Support for [Actors APIs](https://developer.code42.com/api/#tag/Actors), including:
  - An `actors.v1` client to the SDK with the following methods:
    - `client.actors.v1.get_page()` - to query a single page of actors.
    - `client.actors.v1.iter_all()` - to lazily iterate through all pages of actors.
    - `client.actors.v1.get_actor_by_id()` - to retrieve details of a single actor by ID.
    - `client.actors.v1.get_actor_by_name()` - to retrieve details of a single actor by name.
    - `client.actors.v1.get_family_by_member_id()` - to retrieve details of an actor family by a member's ID.
    - `client.actors.v1.get_family_by_member_name()` - to retrieve details of an actor family by a member's name.
  - A set of `actors` CLI commands:
    - `incydr actors list` to list all actors matching search criteria (in table, CSV, or JSON formats).
    - `incydr actors show` to show details of a given actor by ID or name.
    - `incydr actors show-family` to show details of an actors family.

### Removed

- **Breaking Change!** Cloud alias risk profile functionality has been removed.
  - The following Python SDK methods have been removed:
    - `client.user_risk_profiles.add_cloud_alias()` should be replaced by `client.actors.create_adoption()`
    - `client.user_risk_profiles.remove_cloud_alias()` should be replaced by `client.actors.remove_adoption()`
  - The following CLI commands have been removed.
    - `incydr risk-profiles add-cloud-alias` should be replaced by `incydr actors adoption create`
    - `incydr risk-profiles remove-cloud-alias` should be replaced by `incydr actors adoption remove`
    - `incydr risk-profiles bulk-add-cloud-aliases`
    - `incydr risk-profiles bulk-remove-cloud-aliases`

### Changed

- **Breaking Change!** `User risk profiles` have been renamed as `Risk profiles` to better fit their additional application to actors.
  - The SDK has been updated to reflect this via the following changes:
    - `UserRiskProfile` model has been renamed to `RiskProfile`.
    - `UserRiskProfilesPage` model has been renamed to `RiskProfilesPage`.
    - The `UserRiskProfiles` class has been renamed to `RiskProfiles`
    - The Incydr client `user_risk_profiles` property has been renamed to `risk_profiles`, methods in that client have been renamed similarly.
      - `client.user_risk_profiles.v1.get_user_risk_profile()` would now be `client.risk_profiles.v1.get_risk_profile()`.
    - The CLI has been updated to reflect this via the following changes:
      - The `risk-profiles` command group is no longer available under the `users` command group. It is still accessible as its own `incydr` command group. ex: `incydr risk-profiles list`.

### Deprecated

- Alerts Python SDK methods and the Alerts CLI commands group have been deprecated.  Functionality is replaced by the Sessions SDK client and CLI command group.

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
