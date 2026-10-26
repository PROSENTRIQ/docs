# Integrations

Prosentriq sends incidents, actions and safety events to the tools your team
already uses. Add a destination in **Integrations → Add a destination**, then
use **Send test** to check delivery.

## Destinations

| Kind (`kind`) | Plan | Configuration |
|---|---|---|
| Slack (`slack`) | Every plan | `webhook_url` (an incoming webhook, `https://hooks.slack.com/…`) |
| Microsoft Teams (`teams`) | Every plan | `webhook_url` (a Teams workflow or incoming webhook URL). Sent as an Adaptive Card |
| Signed webhook (`webhook`) | Every plan | `url`, optional `secret` (16–256 characters; generated if you leave it out), optional extra `headers` |
| PagerDuty (`pagerduty`) | Pro | `routing_key` (Events API v2 integration key), `region` `us` or `eu` |
| Opsgenie (`opsgenie`) | Pro | `api_key`, `region` `us` or `eu` |
| Syslog (`syslog`) | Pro | `host`, `port` (default 6514), `protocol` `tls` (default), `tcp` or `udp`, `format` `cef` (default) or `json` |
| Splunk HEC (`splunk_hec`) | Pro | `url`, `token`, optional `index`, `sourcetype` (default `prosentriq:alert`) |
| Elastic (`elastic`) | Pro | `url`, `api_key`, `index` (default `prosentriq-alerts`). Documents are ECS-shaped, sent through `_bulk` |
| Microsoft Sentinel (`sentinel`) | Pro | `azure_tenant_id`, `client_id`, `client_secret`, `dce_endpoint`, `dcr_immutable_id`, `stream_name` (default `Custom-ProsentriqAlerts_CL`). Uses the Logs Ingestion API |
| Jira (`jira`) | Pro | `base_url`, `email`, `api_token`, `project_key`, `issue_type` (default `Task`) |
| ServiceNow (`servicenow`) | Pro | `instance_url` (`https://<instance>.service-now.com`), `username`, `password`, optional `assignment_group` |
| OpenTelemetry (`otlp`) | Pro | `endpoint` (an OTLP/HTTP logs endpoint ending in `/v1/logs`), optional `headers` |

The exact JSON schema of every kind is served by `GET /v2/destinations/kinds`.

Credentials (webhook URLs, tokens, secrets, passwords) are encrypted at rest
and never shown again. Changing where a destination sends (its URL, host or
tenant) needs its credential re-entered, so a stored credential can never be
redirected to another server.

Destinations on the hosted service must be public addresses: Prosentriq refuses
to connect to private, loopback and link-local addresses, and never follows
redirects.

## What is sent

Each destination chooses a minimum severity (`min_severity`, default
`medium`) and the event types it receives (`event_types`):

| Event type | Sent by default | When |
|---|---|---|
| `incident.opened` | ✓ | A new incident |
| `incident.escalated` | ✓ | An incident reached a higher severity tier |
| `incident.updated` | | An incident's status changed |
| `action.enforced` | ✓ | Prosentriq blocked, isolated or froze something |
| `action.suggested` | ✓ | An action is waiting for approval |
| `action.undone` | | An action was undone |
| `breaker.tripped` | ✓ | A circuit breaker tripped; autonomous enforcement is suspended |
| `breaker.reset` | | A breaker was reset |
| `rollout.advanced` | | A rule's canary rollout moved to the next stage |
| `rollout.rolled_back` | | A rule's rollout was rolled back |
| `honeytoken.triggered` | | A honeytoken was used |
| `report.trial_value` | | The Trial Value Report is ready |
| `test` | | **Send test** |

Chat and ticketing destinations get a readable message: a title, the
explanation, the severity, indicator, target, score and ATT&CK techniques, and
a link to the incident in the console.

## Webhooks

A webhook receives the event as JSON:

```json
{
  "type": "incident.opened",
  "severity": "high",
  "tenant_id": "4f0c…",
  "occurred_at": "2026-10-26T09:14:03.120581+00:00",
  "data": {
    "incident_id": "a1b2…",
    "title": "Credential attack from 185.220.101.4",
    "indicator": "185.220.101.4",
    "severity": "high",
    "score": 250.0,
    "status": "open",
    "attack": ["T1110", "T1078"],
    "summary": "…",
    "reasons": [ { "code": "AUTH_SUCCESS_AFTER_FAILURES", "score": 150, "sentence": "Successful login as admin after 23 failures from the same source." } ],
    "first_seen": "2026-10-26T09:02:41+00:00",
    "last_seen": "2026-10-26T09:14:02+00:00"
  }
}
```

`data` depends on the type. Action events carry `kind`, `target` and
`ttl_seconds`, for example. Every request is signed with the destination's
secret in `X-Prosentriq-Signature` and names the event in `X-Prosentriq-Event`
and the delivery in `X-Prosentriq-Delivery`. Verify every request:
[Webhook signatures](../api/signatures.md#verifying-a-webhook-receiver-side).

## Delivery, retries and dead letters

Notifications are written in the same transaction as the change they describe,
so you get one if and only if the change happened. Delivery then:

- times out after 10 seconds;
- retries with exponential backoff and jitter, from 30 seconds doubling up to
  6 hours, for up to 10 attempts. A timeout, `408`, `425`, `429` or `5xx` is retried;
- dead-letters at once on an error that won't fix itself (for example `400` or
  `401`, or a refused address).

Dead letters stay in **Integrations → Dead letters** (`GET /v2/outbox`), where
you can retry them (`POST /v2/outbox/{id}/retry`). **Integrations** also shows
each destination's deliveries over the last 7 days.

Deliveries can arrive more than once, for example after a retry. Use
`X-Prosentriq-Delivery` (webhooks) to drop duplicates.

## On a downgrade

A destination your plan no longer includes keeps its settings but receives
nothing until you upgrade.

## Inbound: SOAR

Your SOAR tool can call Prosentriq back to block, unblock, isolate or release.
See [SOAR response actions](soar.md).
