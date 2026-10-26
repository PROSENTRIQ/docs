# Operating a control plane

For Enterprise customers running their own control plane.

## Processes

One image, several roles:

| Role | Command | Scale |
|---|---|---|
| API | The image's `api` command (gunicorn with uvicorn workers) | Stateless, horizontal |
| Detect worker | `prosentriq worker detect` | Horizontal |
| Egress worker | `prosentriq worker egress` | Horizontal |
| Scheduler | `prosentriq worker scheduler` | Run 2 or more; one leads at a time (Postgres advisory lock) |
| Migrations | `prosentriq migrate` | Once per release, with the owner role |

Small installations can run `prosentriq worker all` (every worker in one process).

## Database

- **Roles.** `prosentriq_owner` runs migrations. `prosentriq_app` serves
  traffic; it is neither a superuser nor the owner, so row-level security always
  applies. Never point the API at the owner role.
- **Migrations** are forward-only and checksummed; editing an applied one
  aborts `migrate`. Each must work with the previous release, because it runs
  while that release is serving. Each statement waits at most
  `PROSENTRIQ_MIGRATION_LOCK_TIMEOUT` (default `5s`) for a lock, and then the
  migration rolls back; run `migrate` again when the blocking query is gone.
- **Events** are partitioned by month. The scheduler creates partitions two
  months ahead and enforces each organization's retention daily.
- **Connections.** Budget API workers × `PROSENTRIQ_DB_POOL_MAX` plus the
  workers. Beyond about 200 connections, put PgBouncer in transaction mode in
  front; the application uses only transaction-local settings, so this is safe.
- **Backups.** Postgres holds everything durable. Back it up with point-in-time
  recovery. Redis needs no backup.

## Redis

Redis holds only ephemeral state: rate-limit windows, correlator windows, and
the record of one-time values already used (TOTP codes, signed SOAR requests).
If it goes down, ingest and the API keep working: rate limits fall back to each
process, correlators are skipped (counted in
`prosentriq_correlator_skipped_total`), and one-time values are recorded in
Postgres instead, so a code can never be replayed during an outage.

Always set a password (`redis://:PASSWORD@host:6379/0`, or `rediss://` for
TLS).

## Secrets and keys

| Setting | Notes |
|---|---|
| `PROSENTRIQ_SECRET_KEYS` | Fernet keys, comma-separated. The first encrypts and all decrypt. To rotate: add the new key first, deploy, then remove the old one once stored credentials have been re-encrypted |
| `PROSENTRIQ_SIGNER` and its key | Ed25519 key for evidence packs, the immunity feed and federation. Check it with `prosentriq signing-key`. To change it, see [Signing keys](signing-keys.md) |
| `PROSENTRIQ_METRICS_TOKEN` | Bearer token for the API's `/metrics` |

## Health and metrics

- `/healthz` (liveness) and `/readyz` (database and Redis).
- `/v2/public/version`: the running version and git SHA.
- `/metrics` on the API (bearer `PROSENTRIQ_METRICS_TOKEN`): ingest, rejects,
  duplicates, HTTP latency by route, `prosentriq_build_info`.
- `/metrics` on each worker, on `PROSENTRIQ_METRICS_PORT` (internal only, no
  token): pipeline latency, batches by result, detections by severity,
  decisions by outcome and risk class, egress results. These counters live in
  the worker processes, so scrape the workers too.
- The scheduler leader publishes platform gauges every 15 seconds:
  `prosentriq_queue_batches{status}`, `prosentriq_queue_oldest_seconds`,
  `prosentriq_outbox_pending`, `prosentriq_outbox_dead`,
  `prosentriq_outbox_oldest_seconds`, `prosentriq_circuit_breakers_open`,
  `prosentriq_event_partitions_ahead`, `prosentriq_sensors{freshness,sensor_type}`,
  `prosentriq_scheduler_leader` and
  `prosentriq_scheduler_job_last_success_timestamp_seconds{job}`. Take `max()`
  across scheduler pods: a standby reports leader 0.
- Workers touch `/tmp/prosentriq-heartbeat` on every loop
  (`PROSENTRIQ_HEARTBEAT_FILE`). A liveness probe on its age catches a hung worker.

**Alert on:**

- `prosentriq_queue_oldest_seconds` above 120
- any `prosentriq_batches_processed_total{result="error"}`
- `prosentriq_egress_deliveries_total{result="fail"}` rising
- any open circuit breaker
- `max(prosentriq_scheduler_leader) == 0` for 5 minutes
- `prosentriq_event_partitions_ahead < 1`
- a drop in fresh sensors

## Routine tasks

```bash
prosentriq set-plan --owner-email owner@example.com --plan enterprise
prosentriq enrollment-key --owner-email owner@example.com
prosentriq refresh-never-block          # pull AWS/GCP/Cloudflare/Fastly ranges now (also daily)
prosentriq drain                        # process the ingest queue in the foreground
prosentriq verify-pack pack.json        # verify an evidence pack
prosentriq verify-audit-chains          # recompute every audit chain now (also daily)
prosentriq restore-tenant --tenant ID [--owner-email E]   # undo an organization deletion (within 30 days)
prosentriq purge-deleted                # purge organizations past their 30 days (also daily)
prosentriq erase-user --email E --ticket REF   # an erasure request received by email
```

Ingest batches that fail 5 times are kept with their error. Dead-lettered
notifications can be retried from the console.

## Abuse limits

| Setting | Default | |
|---|---|---|
| `PROSENTRIQ_INGEST_EVENTS_PER_MINUTE` | 30000 | Per sensor or API key |
| `PROSENTRIQ_V1_SIGNUPS_PER_IP_DAY` | 10 | Legacy v1 sign-ups per client address per day |
| `PROSENTRIQ_V1_SIGNUPS_PER_HOUR` | 300 | Legacy v1 sign-ups across the control plane per hour |

## Logs

`PROSENTRIQ_LOG_FORMAT=json` writes one JSON object per line from the API and
every CLI process, with the id of the request being served.
