# Syslogging

Use the `--output` option with `file-events`, `alerts`, or `audit-log` queries to log the resulting data to a server.

The receiving server can be specified in one of the following formats:

* `PROTOCOL:HOSTNAME:PORT`
* `HOSTNAME:PORT`
* `HOSTNAME`

`PROTOCOL` defaults to TCP, `PORT` defaults to 601.

Available `PROTOCOL` values are as follows:

* `TCP`
* `UDP`
* `TLS-TCP`

!!! note
    TCP protocol is recommended because Incydr's logging messages will often be larger than the max size for UDP protocol.
    Using UDP protocol may result in data being truncated.

## Example Commands

The following command will send the file-events from the past 5 days to the 601 port at the `syslog.example.com` server via TCP protocol.

```bash
incydr file-events search --start P5D --output syslog.example.com
```

Specifying all values for the `output` option would look as follows:

```bash
--output TCP:syslog.example.com:601
```
