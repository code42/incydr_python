
### Prepare your environment:

- Install the [Azure Log Analytics Agent](https://learn.microsoft.com/en-us/azure/azure-monitor/agents/log-analytics-agent)
- Install the [Code42 CLI](https://clidocs.code42.com/en/stable/userguides/gettingstarted.html)
- Configure a Code42 CLI [profile](https://clidocs.code42.com/en/stable/userguides/profile.html) for the `omsagent` user:
    1. Become the `omsagent` user: `sudo su omsagent`
    2. Create a new Code42 CLI profile: `code42 profile create-api-client --name sentinel --server <code42_console_domain> --api-client-id <your_id> --secret <your_secret>`
    3. Test the command you'll be using to ingest Inycdr data, for example: `code42 alerts search --begin 3d --format raw-json`

<aside style="margin: 30px">
<p style="margin-left: 30px">
<b>NOTE:</b> The Code42 CLI will use the <a href=https://keyring.readthedocs.io>keyring</a> python library to store the
API client secret. If the profile creation command prompts <code>Please enter password for encrypted keyring:</code>,
then the default keyring store is an encrypted file, which requires a password on every invocation. To store the secret
in a plaintext flat file run the following commands as the <code>omsagent</code> user:<br>
    - <code>mkdir -p $HOME/.local/share/python_keyring</code><br>
    - <code>echo -e '[backend]\ndefault-keyring=keyrings.alt.file.PlaintextKeyring\n' > $HOME/.local/share/python_keyring/keyringrc.cfg</code>
</aside>

### Configure the Log Analytics Agent (`omsagent`)

Following the steps from [Azure Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/agents/data-sources-json),
below is an example config that ingests Incydr Alerts using the Code42 CLI. The configuration examples can be added to
`/etc/opt/microsoft/omsagent/<workspace id>/conf/omsagent.conf` or in their own separate file in the
`/etc/opt/microsoft/omsagent/<workspace id>/conf/omsagent.d/` folder.

#### The input configuration

```
<source>
  type exec
  command code42 alerts search -b 1d --format raw-json --checkpoint sentinel
  format json
  tag oms.api.incydr
  run_interval 1h
</source>
```

The `code42` command has two important options, the `--format raw-json` output causes the CLI to write each Alert JSON
object to stdout on its own line, and the `--checkpoint sentinel` option tells the CLI to store the last retrieved alert
timestamp in the CLI profile, and subsequent runs will use that checkpoint date as the starting point for the next query.
This prevents duplicate alerts from being ingested, as the query will only search for alerts _after_ the last seen one.

The `tag` config value defines what Custom Log table the events will be written to. Whatever is after `oms.api.` in the
tag will become a new Custom Log table (in this example the table name becomes `incydr_CL`).

#### The output configuration

```
<match oms.api.incydr>
  type out_oms_api
  log_level info

  buffer_chunk_limit 5m
  buffer_type file
  buffer_path /var/opt/microsoft/omsagent/<workspace id>/state/out_oms_api_incydr*.buffer
  buffer_queue_limit 10
  flush_interval 20s
  retry_limit 10
  retry_wait 30s
</match>
```

Once the configuration is saved, restart the `omsagent` by running: `/opt/microsoft/omsagent/bin/service_control restart`.

You should start seeing Incydr alerts being populated in the `incydr_CL` table shortly.

For issues troubleshooting ingest using the Log Analytics agent, see [Microsoft's Troubleshooting FAQ](https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs/Troubleshooting.md).
