# SOAR response actions (Pro)

A SOAR playbook (Splunk SOAR, Cortex XSOAR, Tines, Torq, or your own scripts)
can tell Prosentriq to block, unblock, isolate or release. Every request needs
two independent proofs:

1. an API key with the `soar` scope, and
2. an HMAC signature over the body with your organization's SOAR secret.

The same safety checks as for anything else still apply: a playbook can never
block a public DNS resolver, a cloud provider's ranges, an allowlisted address
or the management plane.

## Set it up

1. **Settings → API keys → Create key**, with the `soar` scope.
2. **Integrations → SOAR response actions → Rotate signing secret**, or
   `POST /v2/soar/secret`. The secret is shown once. Rotating it again stops
   the old one immediately.
3. Store both in your SOAR tool's credential store.

## Send an action

```http
POST /v2/soar/actions
Authorization: Bearer psq_live_…        (soar scope)
Content-Type: application/json
X-Prosentriq-Signature: t=<unix time>,v1=<hex HMAC-SHA256 of "<t>." + body>

{
  "action": "block",
  "target": "203.0.113.9",
  "ttl_seconds": 86400,
  "reason": "Playbook 12: phishing infrastructure",
  "external_id": "case-4411"
}
```

| Field | |
|---|---|
| `action` | `block`, `unblock`, `isolate` or `release` |
| `target` | An IP address or CIDR for `block`/`unblock`; the host's name for `isolate`/`release` |
| `sensor_id` | Required for `isolate` and `release` (the sensor on that host). Optional for `block`/`unblock`: apply on one sensor only. Without it, a block applies fleet-wide |
| `ttl_seconds` | Optional, 60 seconds to 90 days |
| `reason` | Free text, kept in the ledger and the audit log |
| `external_id` | Required. Your case or run id. A second request with the same id returns the first action (`"status": "duplicate"`) instead of acting twice |

The body may be at most 16 KB. A complete Python example is in
[Signatures](../api/signatures.md#signing-a-soar-request-sender-side).

## Responses

| Status | |
|---|---|
| `202` `{"status": "accepted", "action": {…}}` | The action was created. It reaches sensors on their next heartbeat |
| `202` `{"status": "duplicate", "action": {…}}` | An action with this `external_id` already exists |
| `401 bad_signature` | Missing, wrong or expired signature (5-minute window) |
| `402 plan_feature` | Your plan doesn't include SOAR |
| `403 forbidden` | The API key lacks the `soar` scope |
| `409 soar_not_configured` | Rotate a SOAR secret first |
| `409 replayed` | This exact signed request was already processed |
| `409 action_refused` | A safety check refused it; `detail` says which |
| `400 invalid_target` | `target` isn't an IP address or CIDR |

Every SOAR action appears in **Approvals & actions** with origin `soar`, and
can be undone like any other.
