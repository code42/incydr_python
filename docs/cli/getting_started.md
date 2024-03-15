# Getting Started

---

This is a brief user guide for getting started with Incydr CLI tool.  For more details on installation see [Incydr CLI](index.md).

For details on how to migrate from the original [Code42 CLI](https://clidocs.code42.com/en/stable/) to the Incydr CLI, see [Migration](migration.md).

## Authentication

---

To authenticate your CLI tool, configure an API client through the Incydr console and store the client ID, the secret, and the URL as settings.

Settings are loaded in the following priority:

* Shell environment variables
* An .env file in the current working directory
* An .env file in `~/.config/incydr` directory

The following values should be present in one of the above locations:

```bash
INCYDR_API_CLIENT_ID='api-client-key'
INCYDR_API_CLIENT_SECRET='api-client-secret'
INCYDR_URL='api_domain'
```

You must update the `api_domain` value for your specific environment. To find the correct value, identify the URL you use to sign in to the Code42 web console, then note the corresponding **API Domain** value in the table below. Use https for all API requests.

| Console Domain         | API Domain         |
| ---------------------- | ------------------ |
| console.us.code42.com  | api.us.code42.com  |
| console.us2.code42.com | api.us2.code42.com |
| console.ie.code42.com  | api.ie.code42.com  |
| console.gov.code42.com | api.gov.code42.com |


See [Incydr SDK Settings](../sdk/settings.md) for more available settings.

## Output

---

### Rich

The Incydr CLI uses [Rich](https://github.com/Textualize/rich) to format help messages and command outputs.

To disable Rich formatting in your log output, set `INCYDR_USE_RICH=false` in your environment configuration.

If Rich is disabled, outputs will default to JSON format.

### Lists

For lists, data can be output in a rich-formatted `table`, `csv`, `json-pretty`, or `json-lines` format.  In most cases, format defaults to `table` but can be specified with the `--format`/`-f` option.

Table output is intended to be a human-readable summary of the data and may default to a limited number of columns in some cases. CSV output defaults to include all columns. Use the `--columns` option with either `table` or `csv` format to specify which columns should be included.

```bash
incydr users list --columns username,first_name,last_name
```

JSON Lines and CSV formatted outputs can be used in tandem with Incydr [bulk commands](bulk.md) to manage multiple entities at once.

### Single Element

For single element returns, data generally defaults to a rich-formatted output specified as `rich`. Other available formats include `json-pretty`, or `json-lines` and can be specified with the `--format`/`-f` option.

An example of the `rich` output format:

```bash
$ incydr users show foo.bar@gmail.com --format rich

╭─────────── User foo.bar@gmail.com  ────────────╮
│ legacy_user_id: 1                              │
│ user_id: 10                                    │
│ username: foo.bar@gmail.com                    │
│ first_name: Foo                                │
│ last_name: Bar                                 │
│ legacy_org_id: 10042                           │
│ org_id: 100                                    │
│ org_guid: 000-000-000                          │
│ org_name: Test-Org                             │
│ notes: None                                    │
│ active: True                                   │
│ blocked: False                                 │
│ creation_date: 2022-11-17T21:05:52.781000Z     │
│ modification_date: 2022-11-17T21:05:52.781000Z │
╰────────────────────────────────────────────────╯
```

An example of the `json-pretty` output format:

```bash
$ incydr users show foo.bar@gmail.com --format json-pretty

{
  "legacyUserId": "1",
  "userId": "10",
  "username": "foo.bar@gmail.com",
  "firstName": "Foo",
  "lastName": "Bar",
  "legacyOrgId": "14405",
  "orgId": "100",
  "orgGuid": "000-000-000",
  "orgName": "Test-Org",
  "notes": null,
  "active": true,
  "blocked": false,
  "creationDate": "2022-11-17T21:05:52.781000Z",
  "modificationDate": "2022-11-17T21:05:52.781000Z"
}
```
Using `--format json-lines` would output the same data as `json-pretty` without any whitespace formatting.

More details on [JSON Lines format](https://jsonlines.org).
