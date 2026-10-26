# Log sources: firewalls, IDS, sshd and your current EDR

The log relay turns syslog from network devices and servers into Prosentriq
events. It ships in the [Python SDK](https://github.com/PROSENTRIQ/prosentriq-sdk-python)
as `prosentriq-sensor relay`. Log relays are free on every plan.

## Accepted input

- Syslog over UDP and TCP: RFC 3164 and RFC 5424, with RFC 6587 framing on TCP
- CEF (ArcSight Common Event Format) from firewalls and security tools
- Suricata EVE JSON
- OpenSSH authentication lines (failed and accepted logins), from syslog or a tailed file

## Install and enroll

The SDK needs Python 3.9 or later.

```bash
pip install --pre prosentriq-sdk
```

`--pre` is needed while the current release is a pre-release (2.0.0rc2).

Create an enrollment key (**Sensors → Create enrollment key**), save it to a
file, then enroll the relay once:

```bash
prosentriq-sensor enroll --api-base https://api.prosentriq.com --enroll-key-file key.txt \
    --type log_relay --out relay.json
```

The key can also come from `PROSENTRIQ_ENROLL_KEY`, or from stdin with
`--enroll-key-file -`. It never needs to appear in the process list.
`relay.json` holds the sensor's credential: keep it readable only by the user
that runs the relay.

## Run the relay

```bash
prosentriq-sensor relay --config relay.json --listen 0.0.0.0:5514 --tail /var/log/auth.log
```

Point your devices' syslog at port 5514 (UDP or TCP). `--tail` follows local
files as well. `prosentriq-sensor relay --help` lists every option.

Run it under systemd or your process supervisor so it restarts. Events are
batched, compressed and retried, with an on-disk spool for outages.

## Side-by-side with your current tool

To evaluate Prosentriq against the product you use today, feed that product's
alerts through the relay and mark them as the incumbent's:

1. Create an API key with the `ingest` scope (**Settings → API keys**).
2. Add it to `relay.json` as `ingest_api_key`.
3. Run the relay with `--incumbent VENDOR` (the vendor's name).

The incumbent's alerts then feed the displacement report instead of being
scored as detections. See [Side-by-side evaluation](../guides/evaluation.md).
