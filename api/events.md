# Sending events

Every sensor (the Linux engine, Kubernetes, log relays, cloud collectors and
yours) sends events to the same door: `POST /v2/events`. Events follow the
open, OCSF-aligned [Prosentriq event schema](https://github.com/PROSENTRIQ/prosentriq-sdk-python/blob/main/schema/prosentriq-event.schema.json).
Every control plane also serves it at `GET /v2/public/schema`.

## Request

```http
POST /v2/events
Authorization: Bearer psqs_…            (a sensor credential, or an API key with the ingest scope)
Content-Type: application/json
Content-Encoding: gzip                   (optional)

{ "events": [ { … }, { … } ] }
```

- 1 to 1,000 events per batch, and at most 5 MB after decompression. One event
  may be at most 16 KB.
- `Content-Encoding` must be `gzip` or absent.
- **Retries are free.** An event is identified by `metadata.uid` and `time`
  within your organization, so sending it again is counted as a duplicate,
  never twice. Give every event a stable `uid`, for example a hash of the
  source record.
- `time` is epoch milliseconds or an ISO 8601 string. It may be at most 10
  minutes in the future (check the sensor's clock) and at most 30 days in the
  past.
- Your organization is always taken from the credential, never from the payload.

## Response

`202 Accepted`, even when some events were rejected:

```json
{
  "accepted": 998,
  "duplicates": 1,
  "rejected": 1,
  "errors": [ { "index": 17, "error": "prosentriq.host_id: Field required" } ],
  "batch_id": 81234
}
```

`errors` lists up to 100 rejected events by their position in the batch. If
no event in the batch is valid the answer is `400 all_rejected`. Other errors:
`400 bad_json`, `400 bad_batch`, `400 bad_gzip`, `413 batch_too_large`,
`413 too_large`, `415 unsupported_encoding`, and `429 ingest_quota` (more than
30,000 events a minute from one credential; wait for `Retry-After`).

Accepted events are processed asynchronously. Detections usually appear within
seconds.

## The event

Four fields are required: `class_uid`, `time`, `metadata.uid` and the
`prosentriq` extension.

```json
{
  "class_uid": 3002,
  "activity_id": 1,
  "time": 1792300800000,
  "severity_id": 3,
  "status_id": 2,
  "message": "Failed password for admin from 185.220.101.4 port 51122 ssh2",
  "metadata": { "uid": "sshd-7f3a9c…", "product": { "name": "my-sensor", "vendor_name": "Example Co" } },
  "prosentriq": { "sensor_type": "sdk", "os": "linux", "host_id": "bastion-1" },
  "src_endpoint": { "ip": "185.220.101.4", "port": 51122 },
  "dst_endpoint": { "ip": "10.0.4.12", "port": 22 },
  "actor": { "user": { "name": "admin" } }
}
```

### Event classes

| `class_uid` | OCSF class | Typical source |
|---|---|---|
| 1001 | File System Activity | File integrity monitoring, ransomware tripwires |
| 1007 | Process Activity | Process starts, profiler |
| 2004 | Detection Finding | A finding from a sensor or another security tool |
| 3002 | Authentication | sshd, console and SSO logins |
| 4001 | Network Activity | Flows, firewall logs, VPC Flow Logs |
| 4002 | HTTP Activity | Web servers, proxies |
| 4003 | DNS Activity | DNS queries |
| 6003 | API Activity | Cloud audit logs (CloudTrail) |

### Common fields

| Field | |
|---|---|
| `activity_id` | The OCSF activity within the class (0–99) |
| `severity_id` | 0–6. The SDK uses 1 info, 2 low, 3 medium, 4 high, 5 critical |
| `status_id` | OCSF status, for example success or failure of a login |
| `message` | Free text, at most 2,048 characters |
| `src_endpoint`, `dst_endpoint` | `ip` (IPv4 or IPv6), `port`, `hostname` |
| `actor` | `user` (`name`, …) and related identity fields |
| `process` | `name`, `pid`, `cmd_line`, `user`, … |
| `file` | `path`, … |
| `query` | DNS query (`hostname`) |
| `traffic` | `bytes_in`, `bytes_out`, … |
| `finding` | `title`, … for class 2004 |
| `cloud`, `api` | Provider, region, account, service and operation for class 6003 |
| `unmapped` | Anything else you want to keep with the event |

### The `prosentriq` extension

| Field | Required | |
|---|---|---|
| `sensor_type` | Yes | `linux_engine`, `kubernetes`, `log_relay`, `cloud_collector`, `windows`, `macos` or `sdk` |
| `os` | Yes | For example `linux` (at most 32 characters) |
| `host_id` | Yes | The host or source this event is about (at most 128 characters) |
| `signal` | No | A finding the sensor already made, for example `PORT_SCAN_DETECTED` |
| `signal_details` | No | Values for the signal's sentence, for example `{"unique_ports": 40}` |
| `k8s` | No | Pod, namespace and image, set by the Kubernetes sensor |

The `signal` codes the control plane scores are listed in
[Detections](../concepts/detections.md#reasons). Use one when your sensor has
already recognised the pattern; otherwise send the raw events and let the
control plane correlate them.

## With the Python SDK

The [SDK](https://github.com/PROSENTRIQ/prosentriq-sdk-python) builds valid
events, batches and gzips them, retries with backoff, and spools to disk while
the control plane is unreachable:

```python
from prosentriq_sdk import Client, events

client = Client("https://api.prosentriq.com", token)   # a sensor credential or an ingest API key
client.send([
    events.auth("185.220.101.4", user="admin", success=False, host_id="bastion-1"),
    events.network("10.0.4.12", "203.0.113.9", dst_port=4444, host_id="bastion-1"),
])
```

Builders: `network`, `auth`, `process_start`, `file_activity`, `dns_query`,
`cloud_api` and `finding`. Pass `uid=events.stable_uid(...)` built from the
source record so re-reading a log never double-counts.

See also [Your own sensor](../install/custom-sensor.md).
