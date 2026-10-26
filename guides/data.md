# Your data: retention, export and deletion

## What Prosentriq stores

- **Events** your sensors send: network, process, file, authentication, DNS
  and cloud API activity, as described in the [event schema](../api/events.md).
  Sensors send findings and summarised activity, not raw packets.
- **What Prosentriq made of them**: detections, incidents, decisions, actions,
  reports and evidence packs.
- **Your configuration**: members, rules, allowlist, destinations (credentials
  encrypted), honeytokens and settings.
- **The audit log** of privileged actions, hash-chained.

Each organization's data is isolated by the database itself (Postgres
row-level security). The [Privacy Policy](https://prosentriq.com/legal/privacy)
covers personal data in detail.

## Retention

| Plan | Events kept for |
|---|---|
| Free | 14 days |
| Starter | 30 days |
| Pro | 90 days |
| Enterprise | 400 days |

Older events are deleted daily. After a downgrade, your previous, longer
retention is kept for 30 days.

## Export

- Any list can be read through the [API](../api/README.md) (events, incidents,
  decisions, actions, the audit log), for example into your SIEM.
- [Integrations](integrations.md) stream incidents and actions as they happen.
- **Evidence packs** are signed snapshots of a period ([Compliance](compliance.md)).
- **Configuration**: `GET /v2/migrate/export` ([Evaluation and migration](evaluation.md#export-and-import-your-configuration)).

## Deleting an organization

An owner deletes the organization in **Settings → Organization** (or
`POST /v2/tenant/delete`). You are asked to prove it's you again: a stolen
session alone can never delete anything.

- Access stops immediately for everyone, and sensors stop being accepted.
- The data is purged after **30 days**. Until then it can be restored:
  contact support@prosentriq.com.
- Deleting the organization doesn't cancel a paid subscription by itself:
  cancel it first in **Settings → Usage & migration → Manage billing**. The
  organization's audit log is purged with it.

## Deleting your account

**Settings → My security → Delete my account…** (or `GET /v2/account/deletion` to
see what it would do, then `POST /v2/account/delete`). Your account is erased
at once. It can't be deleted while you are the only owner of an organization
that has other members or customer organizations: hand ownership to someone
else first, or delete the organization.

Kept afterwards, as the Privacy Policy explains: your email with the document
versions you accepted and when, for legal claims, for 6 years; and entries in
an organization's audit log that name you, because rewriting them would break
the chain. Those go when that organization is purged.

## Prosentriq staff access

Without a grant from an owner, Prosentriq staff can't see your incidents,
hosts or integrations. See [Support access](access.md#support-access).
