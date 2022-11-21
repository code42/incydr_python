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

## Alerts
---

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

## Devices
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

## Legal Hold
---

### `Policy` model

::: incydr.models.Policy
    :docstring:

### `Matter` model

::: incydr.models.Matter
    :docstring:

### `Custodian` model

::: incydr.models.Custodian
    :docstring:

### `CustodianMembership` model

::: incydr.models.CustodianMembership
    :docstring:

### `MatterMembership` model

::: incydr.models.MatterMembership
    :docstring:

## Roles
---

### `Role` model

::: incydr.models.Role
    :docstring:

### `UpdateRolesResponse` model

::: incydr.models.UpdateRolesResponse
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

## User Risk Profiles
---

### `UserRiskProfile` model

::: incydr.models.UserRiskProfile
    :docstring:

### `UserRiskProfilesPage` model

::: incydr.models.UserRiskProfilesPage
    :docstring:

## Watchlists
---

### `Watchlist` model

::: incydr.models.Watchlist
    :docstring:

### `WatchlistsPage` model

::: incydr.models.WatchlistsPage
    :docstring:

### `WatchlistUser` model

::: incydr.models.WatchlistUser
    :docstring:

### `WatchlistMembersList` model

::: incydr.models.WatchlistMembersList
    :docstring:

### `IncludedUsersList` model

::: incydr.models.IncludedUsersList
    :docstring:

### `ExcludedUsersList` model

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
