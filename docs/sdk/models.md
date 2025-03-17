# Models

!!! note
    Incydr SDK's Pydantic models default to snake_case for all field attribute names for consistency, and by default will
    convert names to the casing expected by the API endpoint when serializing the data using the model's `.json()` and
    `.dict()` methods.

    For example, if the server returns a response with a JSON key of `createdAt`, the value will be accessible on the
    model via `Model.created_at`, but calling `Model.json()` will output with a key of `createdAt` so the data can be
    used in further requests.

    Fields where a transormation has been applied are marked with `json_alias=<aliasName>` below.

See [Pydantic documentation](https://pydantic-docs.helpmanual.io/usage/models/#model-properties) for full list of
available model methods.

## Actors
---

### `Actor` model

::: incydr.models.Actor
    :docstring:

### `ActorFamily` model

::: incydr.models.ActorFamily
    :docstring:

### ActorsPage` model

::: incydr.models.ActorsPage
    :docstring:

## Agents
---

### `Agent` model

::: incydr.models.Agent
    :docstring:

### `AgentsPage` model

::: incydr.models.AgentsPage
    :docstring:

## Alerts (Deprecated)
---

Alerts has been replaced by [Sessions](#sessions).

### `AlertDetails` model

::: incydr.models.AlertDetails
    :docstring:

### `AlertSummary` model

::: incydr.models.AlertSummary
    :docstring:

### `AlertQueryPage` model

::: incydr.models.AlertQueryPage
    :docstring:

## Alert Rules
---

### `RuleUser` model

::: incydr.models.RuleUser
    :docstring:

### `RuleUsersList` model

::: incydr.models.RuleUsersList
    :docstring:

### `RuleDetails` model

::: incydr.models.RuleDetails

## Audit Log
---

### `AuditEventsPage` model

::: incydr.models.AuditEventsPage
    :docstring:

## Cases
---

### `Case` model

::: incydr.models.Case
    :docstring:

### `CasesPage` model

::: incydr.models.CasesPage
    :docstring:

### `CaseFileEvents` model

::: incydr.models.CaseFileEvents
    :docstring:

## Customer
---

### `Customer` model

::: incydr.models.Customer
    :docstring:

## Departments
---

### `DepartmentsPage` model

::: incydr.models.DepartmentsPage
    :docstring:

## Devices (Deprecated)

Devices has been replaced by [Agents](#agents).

---

### `Device` model

::: incydr.models.Device
    :docstring:

### `DevicesPage` model

::: incydr.models.DevicesPage
    :docstring:

## Directory Groups
---

### `DirectoryGroup` model

::: incydr.models.DirectoryGroup
    :docstring:

### `DirectoryGroupsPage` model

::: incydr.models.DirectoryGroupsPage
    :docstring:

## File Events
---

### `FileEvent` model

::: incydr.models.FileEventV2
    :docstring:

### `FileEventsPage` model

::: incydr.models.FileEventsPage
    :docstring:

### `SavedSearch` model

::: incydr.models.SavedSearch
    :docstring:

## Roles
---

### `Role` model

::: incydr.models.Role
    :docstring:

### `UpdateRolesResponse` model

::: incydr.models.UpdateRolesResponse
    :docstring:

## Sessions

::: incydr.models.Session
    :docstring:

::: incydr.models.SessionsPage
    :docstring:

## Trusted Activities
---

### `TrustedActivity` model

::: incydr.models.TrustedActivity
    :docstring:

### `TrustedActivitiesPage` model

::: incydr.models.TrustedActivitiesPage
    :docstring:

## Users
---

### `User` model

::: incydr.models.User
    :docstring:

### `UsersPage` model

::: incydr.models.UsersPage
    :docstring:

### `Role` model

:::incydr.models.Role
    :docstring:

## Risk Profiles (Deprecated)

Risk Profiles have been replaced by [Actors](#actors).

---

### `RiskProfile` model

::: incydr.models.RiskProfile
    :docstring:

### `RiskProfilesPage` model

::: incydr.models.RiskProfilesPage
    :docstring:

## Watchlists
---

### `Watchlist` model

::: incydr.models.Watchlist
    :docstring:

### `WatchlistsPage` model

::: incydr.models.WatchlistsPage
    :docstring:

### `WatchlistActor` model

::: incydr.models.WatchlistActor
    :docstring:

### `WatchlistUser` model

WatchlistUser is deprecated. Use WatchlistActor instead.

::: incydr.models.WatchlistUser
    :docstring:

### `WatchlistMembersListV2` model

::: incydr.models.WatchlistMembersListV2
    :docstring:

### `WatchlistMembersList` model

WatchlistMembersList is deprecated. Use WatchlistMembersListV2 instead.

::: incydr.models.WatchlistMembersList
    :docstring:

### `IncludedActorsList` model

::: incydr.models.IncludedActorsList
    :docstring:

### `ExcludedActorsList` model

::: incydr.models.ExcludedActorsList
    :docstring:

### `IncludedUsersList` model

IncludedUsersList is deprecated. Use IncludedActorsList instead.

::: incydr.models.IncludedUsersList
    :docstring:

### `ExcludedUsersList` model

ExcludedUsersList is deprecated. Use ExcludedActorsList instead.

::: incydr.models.ExcludedUsersList
    :docstring:

### `IncludedDepartmentsList` model

::: incydr.models.IncludedDepartmentsList
    :docstring:

### `IncludedDepartment` model

::: incydr.models.IncludedDepartment
    :docstring:

### `IncludedDirectoryGroupsList` model

::: incydr.models.IncludedDirectoryGroupsList
    :docstring:

### `IncludedDirectoryGroup` model

::: incydr.models.IncludedDirectoryGroup
    :docstring:
