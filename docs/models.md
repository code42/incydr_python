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

## Cases
---

### `Case` model

::: incydr.models.Case
    :docstring:

### `CasesPage` model

::: incydr.models.CasesPage
    :docstring:


## Customer
---

### `Customer` model

::: incydr.models.Customer
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

### `SavedSearchesPage` model

::: incydr.models.SavedSearchesPage
    :docstring:
