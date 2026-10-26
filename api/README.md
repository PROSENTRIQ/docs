# API overview

Everything the console does goes through the same public API, so you can
automate all of it.

- Base URL: `https://api.prosentriq.com`, or your own control plane's API URL
- Format: JSON, UTF-8. `POST /v2/events` also accepts a gzip body
- Specification: OpenAPI 3 at `GET /v2/openapi.json` on every control plane, and
  a snapshot in this repository: [openapi.json](openapi.json)
- Versioning: everything under `/v2` is the current API. `/v1/*` is a frozen
  compatibility API for agents deployed before v2. It keeps working, but don't
  build anything new on it.

## Authentication

Send a bearer token:

```bash
curl -H "Authorization: Bearer psq_live_…" https://api.prosentriq.com/v2/incidents
```

| Token | Prefix | Who uses it | Created in |
|---|---|---|---|
| API key | `psq_live_` | Scripts, SIEM pulls, CI, SOAR tools | **Settings → API keys** |
| Sensor credential | `psqs_` | One sensor. It can send events, heartbeat and read the immunity feed, and nothing else | Issued when a sensor enrolls |
| Enrollment key | `psqe_` | Only to enroll a sensor (`POST /v2/sensors/enroll`) | **Sensors → Create enrollment key** |

Only a hash of every token is stored. A token is shown once, when it is
created. Revoke API keys in Settings and retire sensors on the Sensors page;
both take effect at once.

The console signs in with a session cookie plus a CSRF header. Integrations
should always use API keys.

### API key scopes

An API key carries one or more scopes:

| Scope | Grants | For |
|---|---|---|
| `read` | `read` | Dashboards, SIEM pulls, reporting |
| `write` | `read`, `triage`, `respond`, `manage_rules` | Automation that triages incidents, approves or undoes actions, blocks, and manages rules |
| `admin` | Everything an admin can do (below) | Full automation of an organization |
| `ingest` | `ingest` | Sending events (`POST /v2/events`) and incumbent alerts |
| `soar` | `soar` | Signed inbound SOAR actions (`POST /v2/soar/actions`) |

Give each key the fewest scopes it needs. `ingest` and `soar` are only
available to API keys, not to people.

### Roles and permissions

People get a role per organization:

| Permission | Owner | Admin | Analyst | Auditor |
|---|---|---|---|---|
| `read`: dashboards, events, incidents, ledger | ✓ | ✓ | ✓ | ✓ |
| `triage`: incident status, approve or reject suggestions, undo | ✓ | ✓ | ✓ | |
| `respond`: manual block, unblock, isolate | ✓ | ✓ | ✓ | |
| `manage_rules`: rules, rollouts, allowlist, honeytokens, migration | ✓ | ✓ | ✓ | |
| `manage_autonomy`: the dial, breaker limits and reset | ✓ | ✓ | | |
| `manage_integrations`: destinations, SOAR secret | ✓ | ✓ | | |
| `manage_sensors`: enrollment keys, sensor mode, retire sensors | ✓ | ✓ | | |
| `manage_members`: invites, roles, MSP customer organizations | ✓ | ✓ | | |
| `manage_keys`: API keys | ✓ | ✓ | | |
| `manage_tenant`: SSO, branding, organization settings, deletion, support access | ✓ | | | |
| `compliance`: generate and download evidence, auditor links | ✓ | ✓ | | ✓ |

You can never give anyone a role higher than your own. See
[Teams and access](../guides/access.md).

### Managed service providers

An MSP's API key or member acts in one of its customer organizations by
sending that organization's id:

```bash
curl -H "Authorization: Bearer psq_live_…" -H "X-Prosentriq-Tenant: <customer org id>" \
     https://api.prosentriq.com/v2/incidents
```

MSP members act in customer organizations with their MSP role, capped at
admin. Ownership of a customer organization stays with the customer. List
customer organizations with `GET /v2/msp/tenants`.

## Errors

Every error has the same shape:

```json
{
  "error": { "code": "forbidden", "message": "missing permission: manage_rules", "detail": null },
  "request_id": "6f1c…"
}
```

| Status | Typical `code` | Meaning |
|---|---|---|
| 400 | `invalid_target`, `bad_json`, `bad_batch`, … | The request is wrong; `message` says how |
| 401 | `unauthenticated`, `invalid_credentials`, `bad_signature` | No valid token, or a bad signature |
| 402 | `plan_feature` | Your plan doesn't include this. `detail.required_plan` is the cheapest plan that does |
| 403 | `forbidden`, `tenant_forbidden` | Your token or role lacks a permission |
| 404 | `not_found` | |
| 409 | `replayed`, `soar_not_configured`, … | A conflict with the current state |
| 413 | `too_large`, `batch_too_large` | The body or batch is over a limit |
| 422 | `invalid_request` | Validation failed; `detail` lists each field |
| 429 | `rate_limited`, `ingest_quota` | Slow down. Retry after the `Retry-After` header's seconds |
| 5xx | | Retry with backoff. Quote `request_id` to support |

You may send your own `X-Request-Id` (a short plain token). It is echoed in the
response and in our logs. Otherwise one is generated.

## Limits

| Limit | Value |
|---|---|
| Request body | 5 MB (after gzip decompression) |
| Events per batch | 1,000 |
| Size of one event | 16 KB |
| Events per minute, per sensor or API key | 30,000 (hosted default) |
| SOAR request body | 16 KB |

Sign-in, sign-up, password reset and public verification endpoints are also
rate-limited per client address.

## Lists and pagination

List endpoints return the newest items first, as a JSON array. They take
`limit`, and the large ones take `before` (an ISO 8601 timestamp). To page
back, pass the timestamp of the last item you received as `before`:

| List | Sorted by, and `before` compares with |
|---|---|
| `GET /v2/events` | `time` |
| `GET /v2/incidents` | `last_seen` |
| `GET /v2/detections`, `GET /v2/decisions` | `created_at` |

Filters are query parameters, for example
`GET /v2/incidents?status=open&severity=critical&limit=50`.

## Routes

Each route lists the permission it needs. "Sensor" means a sensor credential.
"Public" needs no token.

### Sensors and events

| Route | Permission | Purpose |
|---|---|---|
| `POST /v2/sensors/enroll/validate` | Public (enrollment key in body) | Check an enrollment key without enrolling |
| `POST /v2/sensors/enroll` | Public (enrollment key in body) | Enroll a sensor; returns its credential once |
| `POST /v2/sensors/heartbeat` | Sensor | Report status, acknowledge directives, receive new ones |
| `GET /v2/sensors/immunity-feed` | Sensor | The signed Immunity Network feed |
| `POST /v2/events` | `ingest` | Send up to 1,000 events. See [Sending events](events.md) |
| `GET /v2/sensors` | `read` | List sensors with freshness, mode and version |
| `PATCH /v2/sensors/{id}` | `manage_sensors` | `desired_mode` (`observe`/`enforce`), `autonomy_override` (1–5), `labels` |
| `DELETE /v2/sensors/{id}` | `manage_sensors` | Retire a sensor (its credential stops working) |
| `GET/POST /v2/enrollment-keys`, `DELETE /v2/enrollment-keys/{id}` | `manage_sensors` | Enrollment keys (`max_uses`, `expires_days` 1–365, default 30) |

### Investigate

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/overview` | `read` | The Overview page's numbers |
| `GET /v2/trends` | `read` | Time series for the Overview charts |
| `GET /v2/events` | `read` | Search events (`ip`, `sensor_id`, `class_uid`, `signal`, `since`, `before`, `limit` ≤ 1,000) |
| `GET /v2/detections` | `read` | Detections (`indicator`, `incident_id`, `before`, `limit` ≤ 500) |
| `GET /v2/incidents` | `read` | Incidents (`status`, `severity`, `before`, `limit` ≤ 200) |
| `GET /v2/incidents/{id}` | `read` | One incident with its reasons |
| `GET /v2/incidents/{id}/storyline` | `read` | Time-ordered events, detections, decisions and actions |
| `PATCH /v2/incidents/{id}` | `triage` | `status`: `open`, `acknowledged`, `resolved` or `false_positive`, with a `note` |
| `POST /v2/incidents/{id}/explain` | `read` | Ask the AI investigation assistant (Pro; off until an owner turns it on) |
| `GET /v2/actors/{indicator}` | `read` | Everything known about one address or actor |

### Autonomy and response

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/autonomy` | `read` | The dial, the effective level and why, breaker state |
| `PUT /v2/autonomy` | `manage_autonomy` | Set the level (1–5) with a `reason` |
| `PUT /v2/autonomy/breaker-limits` | `manage_autonomy` | `max_blocks_per_minute`, `max_sensor_blocks_per_minute`, `max_undos_per_hour`, `cooldown_minutes` |
| `POST /v2/autonomy/breakers/{scope}/reset` | `manage_autonomy` | Reset a tripped circuit breaker after its cool-down |
| `GET /v2/decisions` | `read` | The decision ledger (`outcome`, `indicator`, `before`, `limit` ≤ 500) |
| `GET /v2/actions` | `read` | Actions (`status`, `limit` ≤ 500) |
| `POST /v2/actions` | `respond` | Manual `block_ip`, `unblock_ip`, `isolate_host` or `release_host`, with `target`, `sensor_id` (required to isolate or release a host), `ttl_seconds` (60 s to 90 days) and `reason` |
| `POST /v2/actions/{id}/approve`, `/reject` | `triage` | Decide a suggested action |
| `POST /v2/actions/{id}/undo` | `triage` | Undo an enforced action (`note`, `false_positive`) |
| `GET/POST /v2/allowlist`, `DELETE /v2/allowlist/{id}` | `read` / `manage_rules` | Addresses and ranges Prosentriq never blocks |
| `GET /v2/never-block` | `read` | The global never-block list (major resolvers, cloud provider ranges) |
| `POST /v2/blast-radius/check` | `read` | Ask whether a target would pass the blast-radius check |

### Rules and honeytokens

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/rules`, `GET /v2/rules/{id}` | `read` | Built-in, imported and custom rules |
| `POST /v2/rules` | `manage_rules` | Create a custom rule (a draft) |
| `POST /v2/rules/import` | `manage_rules` | Import Sigma or Falco rules (Pro) |
| `PATCH/DELETE /v2/rules/{id}` | `manage_rules` | Edit or delete a rule |
| `POST /v2/rules/{id}/rollout` | `manage_rules` | Start the canary rollout |
| `POST /v2/rules/{id}/rollback` | `manage_rules` | Roll a rule back by hand |
| `POST /v2/rules/test` | `read` | Test a rule against recent events |
| `POST /v2/rules/evolve`, `GET /v2/rules/ga/baseline` | `manage_rules` / `read` | Machine-generated rule suggestions |
| `GET/POST /v2/honeytokens`, `DELETE /v2/honeytokens/{id}` | `read` / `manage_rules` | Honeytokens (Pro). See [Honeytokens](../guides/honeytokens.md) |

### Integrations

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/destinations/kinds` | `read` | Every destination kind with its configuration schema, and the event types |
| `GET /v2/destinations` | `read` | Destinations with delivery counts for the last 7 days |
| `POST /v2/destinations` | `manage_integrations` | Add a destination. See [Integrations](../guides/integrations.md) |
| `PATCH/DELETE /v2/destinations/{id}` | `manage_integrations` | Change or remove one |
| `POST /v2/destinations/{id}/test` | `manage_integrations` | Send a test event |
| `GET /v2/outbox`, `POST /v2/outbox/{id}/retry` | `read` / `manage_integrations` | Deliveries and dead letters; retry one |
| `POST /v2/soar/secret` | `manage_integrations` | Create or rotate the SOAR signing secret (shown once) |
| `POST /v2/soar/actions` | `soar` + signature | Inbound SOAR action. See [SOAR](../guides/soar.md) |

### Compliance and reports

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/compliance/frameworks`, `GET /v2/compliance/status` | `read` | Frameworks and live control status |
| `POST /v2/compliance/evidence-packs` | `compliance` | Generate a signed pack (`frameworks`, `days` 1–400, default 90) |
| `GET /v2/compliance/evidence-packs` | `read` | List packs |
| `GET /v2/compliance/evidence-packs/{id}` | `compliance` | Download a pack |
| `POST /v2/compliance/insurance-pack` | `compliance` | Generate a cyber-insurance pack |
| `GET/POST /v2/compliance/auditor-links`, `DELETE …/{id}` | `compliance` | Time-boxed auditor links (Pro) |
| `GET /v2/auditor/{token}`, `GET /v2/auditor/{token}/packs/{id}` | The link's token | What an auditor sees |
| `GET /v2/reports`, `GET /v2/reports/{id}`, `GET /v2/reports/trial-value/preview` | `read` | Trial Value and other reports |
| `POST /v2/displacement/alerts` | `ingest` | Your current tool's alerts, for side-by-side mode |
| `POST /v2/displacement/report` | `read` | The side-by-side displacement report (Pro) |
| `POST /v2/migrate/allowlist`, `GET /v2/migrate/export`, `POST /v2/migrate/import` | `manage_rules` | The migration kit. See [Evaluation and migration](../guides/evaluation.md) |
| `GET /v2/audit-log`, `GET /v2/audit-log/verify` | `read` | The hash-chained audit log, and a check that the chain is intact |
| `GET /v2/usage` | `read` | Enforcing nodes now, daily active sensors and events (`days` ≤ 400), estimated monthly cost |

### Organization and access

| Route | Permission | Purpose |
|---|---|---|
| `GET /v2/tenant` | `read` | The organization, its plan and entitlements |
| `PATCH /v2/tenant` | `manage_tenant` | Name, branding, Immunity Network contribution, ransomware settings, AI assistant opt-in |
| `GET /v2/members` | `read` | Members |
| `POST /v2/members/invites`, `PATCH/DELETE /v2/members/{id}` | `manage_members` | Invite, change role, remove |
| `GET/POST /v2/api-keys`, `DELETE /v2/api-keys/{id}` | `manage_keys` | API keys (`name`, `scopes`) |
| `PUT/DELETE /v2/sso`, `/v2/sso/domains…` | `manage_tenant` | Single sign-on and verified domains (Starter and up) |
| `GET /v2/msp/tenants` | `read` | An MSP's customer organizations |
| `POST /v2/msp/tenants` | `manage_members` | Create a customer organization |
| `POST /v2/msp/tenants/{id}/delete` | `manage_tenant` | Delete a customer organization |
| `GET /v2/support-access` | `read` | Support access grants |
| `POST /v2/support-access`, `DELETE …/{id}` | `manage_tenant` | Let Prosentriq support see your data for 1, 24, 72 or 168 hours; revoke |
| `POST /v2/tenant/delete` | `manage_tenant` + re-authentication | Delete the organization (restorable for 30 days) |
| `GET /v2/billing`, `POST /v2/billing/checkout`, `/subscription`, `/portal` | `read` / signed-in user | Subscription, checkout, plan change and the billing portal |

Account routes (`/v2/auth/*`, `/v2/account/*`) are for people signing in to the
console and are not meant for API keys.

### Public

| Route | Purpose |
|---|---|
| `GET /healthz`, `GET /readyz` | Liveness and readiness |
| `GET /v2/public/version` | Running version and git SHA |
| `GET /v2/public/pricing`, `GET /v2/public/pricing/quote` | Plans, prices and a quote for a node count |
| `GET /v2/public/schema` | The canonical event JSON Schema |
| `GET /v2/public/signing-key` | The control plane's signing key, key history and endorsements |
| `POST /v2/public/evidence/verify` | Verify an evidence pack's signature |
| `GET /v2/public/immunity` | Live Immunity Network counters |
| `GET /v2/public/legal` | Current Terms and Privacy Policy versions |

## SDKs

- Python: [prosentriq-sdk-python](https://github.com/PROSENTRIQ/prosentriq-sdk-python)
  (`pip install --pre prosentriq-sdk`). It covers sensors and sending events.
  For everything else, any HTTP client works with the routes above.
