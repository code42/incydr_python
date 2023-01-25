# Bulk Commands

---

Bulk functionality is available for many CLI commands.  Bulk commands will all contain the `bulk-` prefix in the subcommand.

All bulk methods take a single argument FILE as input in either CSV or [JSON Lines](https://jsonlines.org) format.

File format defaults to CSV.  To specify a [JSON Lines](https://jsonlines.org) file, pass the `--format json-lines` option with a bulk command.
Use `--help` with a bulk command to view the necessary columns/keys for the input file.

CSV files accept common aliases for fields and will perform additional lookups for usernames to simplify passing data between commands.  For example, a command that
requires a `user` column will also accept a column labeled as `userId`, `user_id`, or `username`.

The following example command will update multiple cases:

```bash
incydr cases bulk-update bulk_update_cases.csv
```

Add the `--format` option to pass a [JSON Lines](https://jsonlines.org) formatted file

```bash
incydr cases bulk-update bulk_update_cases.jsonl --format json-lines
```

If there are parsing errors, error messages will be output to the console and more details will be available in the logs
once the command has completed and the entire file has attempted to be parsed.

For more information on logging, see [Logging](logging.md).
