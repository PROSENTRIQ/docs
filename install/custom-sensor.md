# Your own sensor

Anything that can make an HTTPS request can be a Prosentriq sensor: an
appliance, a script, a service that already sees security-relevant activity.
There are two ways to send events:

| | Use when |
|---|---|
| An **API key** with the `ingest` scope | You only send events, from one or many places (**Settings → API keys**) |
| An **enrolled sensor** | You want it listed on the Sensors page with its freshness, and to receive directives (block, isolate) back |

## Send events with an API key

```bash
curl -X POST https://api.prosentriq.com/v2/events \
  -H "Authorization: Bearer $PROSENTRIQ_INGEST_KEY" \
  -H "Content-Type: application/json" \
  -d '{"events":[{"class_uid":3002,"time":"2026-10-26T09:00:00Z","status_id":2,
        "metadata":{"uid":"bastion-1-login-123"},
        "prosentriq":{"sensor_type":"sdk","os":"linux","host_id":"bastion-1"},
        "src_endpoint":{"ip":"185.220.101.4"},"actor":{"user":{"name":"admin"}}}]}'
```

The full request, response and schema: [Sending events](../api/events.md).

## Enroll a sensor with the Python SDK

```bash
pip install --pre prosentriq-sdk
```

```python
from prosentriq_sdk import Client, events

enrolled = Client.enroll("https://api.prosentriq.com", enrollment_key,
                         hostname="appliance-1", sensor_type="sdk", os="linux")
# enrolled = {"sensor_id", "tenant_id", "token", "api_base", "signing_key": {"key_id", "public_key"}}
# Store the token (0600) and pin signing_key.public_key: the token is shown once,
# and enrolling again creates a new sensor.

client = Client("https://api.prosentriq.com", enrolled["token"])
client.send([events.auth("185.220.101.4", user="admin", success=False, host_id="appliance-1")])

hb = client.heartbeat()            # every heartbeat_seconds (30 s by default)
for directive in hb["directives"]:
    ...                            # apply it, then acknowledge it on the next heartbeat
```

Or from the command line, which writes the credential to a file:

```bash
prosentriq-sensor enroll --api-base https://api.prosentriq.com --enroll-key-file key.txt \
    --type sdk --hostname appliance-1 --out sensor.json
```

## Heartbeats and directives

A sensor sends `POST /v2/sensors/heartbeat` every 30 seconds with its version,
its current mode (`observe` or `enforce`), whether it `can_enforce`, its own
address and gateway, and acknowledgements (`acks`) for the directives it has
applied. The answer tells it:

| Field | |
|---|---|
| `desired_mode` | `observe` or `enforce`. Enforce only when the host is set to enforce **and** the plan allows it |
| `autonomy_level` | The effective level for this sensor, and `autonomy_notes` explaining any cap |
| `local_breaker` | Limits for the sensor's own circuit breaker, which keeps working offline |
| `directives` | Actions to apply: each has an `id`, a `kind` and its parameters |
| `immunity_feed` | When the signed Immunity Network feed last changed. Fetch it from `GET /v2/sensors/immunity-feed` |
| `signing_key_id` | The control plane's current signing key |
| `heartbeat_seconds` | How often to heartbeat |

Directive kinds are `block_ip` and `unblock_ip`, `isolate_host` and
`release_host`, and `freeze_process` and `thaw_process`. Acknowledge each one
with `{"id": …, "ok": true}`, or `"ok": false` and an `error`. A directive that
isn't acknowledged is delivered again after 5 minutes, so apply directives
idempotently. Fleet-wide actions go to every sensor that can enforce. A sensor
that cannot enforce should send `can_enforce: false` (the default). It then
receives no directives, and the Sensors page won't let it be set to enforce.

## Verify the Immunity Network feed

The feed is signed with the control plane's Ed25519 key. Pin the key when you
enroll and check every feed against it before using it:

```bash
prosentriq-sensor verify-feed --config sensor.json
```

In code, `prosentriq_sdk.client.verify_feed(feed, pinned_public_key_b64)`. If
the control plane changes its key, it publishes an endorsement signed by the
previous key, and the SDK follows that chain from the key you pinned. See
[Signing keys](../self-hosting/signing-keys.md).

## Good practice

- Give every event a stable `metadata.uid` so retries and re-reads are free.
- Keep the credential file readable only by the sensor's user.
- Send findings as `prosentriq.signal` only when your sensor has really
  recognised the pattern. Otherwise send the raw events.
- Licence: the SDK is Apache-2.0. Read and change it as you like.
