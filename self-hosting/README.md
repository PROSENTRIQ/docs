# Self-hosting the control plane (Enterprise)

On Enterprise you can run the same control plane we run, in your own
infrastructure: in your cloud account, on premises, or air-gapped. No feature
is held back.

## Getting the software

Self-hosting is part of an Enterprise agreement (sales@prosentriq.com). With
it you get:

- access to the control plane and console images (`ghcr.io/prosentriq/platform`
  and `ghcr.io/prosentriq/console`), signed like every release
- the deployment bundle: the Helm chart `prosentriq-platform`, the Docker
  Compose deployment, systemd units, and the database role script
- onboarding help and the 24/7 support SLA

The sensors are the same public packages, chart and SDK as for the hosted
service. Point them at your control plane with `--api-base` (installer),
`apiBase` (Helm) or `--api-base` (SDK).

## Topologies

| | When | What runs |
|---|---|---|
| **Kubernetes** (Helm) | Production, high availability | API (autoscaled), detect and egress workers (autoscaled, optionally on queue depth with KEDA), schedulers, the console. Bring your own Postgres and Redis |
| **One VM** (Docker Compose) | Small fleets, labs, single sites | Everything, with Postgres 16 and Redis 7, on one host. The console and API are served together on port 8080 behind your TLS reverse proxy |
| **Bare metal** (systemd) | Where containers aren't wanted | The same processes as systemd units, behind nginx |
| **Air-gapped** | No internet access | Any of the above, plus a local signing key, a private Immunity hub, an offline package mirror, and the AI assistant off |

## Requirements

| | |
|---|---|
| Postgres | 14 or later (16 recommended). Install postgresql-contrib for the `pg_trgm` extension |
| Redis | 7 or later, with a password. Holds only ephemeral state |
| Signing key | A local Ed25519 key, or AWS KMS, Google Cloud KMS or Vault Transit ([Signing keys](signing-keys.md)) |
| Mail | An SMTP server, for invitations, password resets and reports |
| TLS | A reverse proxy or load balancer in front, terminating HTTPS |

## Configuration

Every setting is an environment variable starting with `PROSENTRIQ_`. With
`PROSENTRIQ_ENV=production` the control plane **refuses to start** with an
unsafe configuration: no secret keys, no SMTP, no signing key, debug endpoints
on, non-HTTPS URLs, or a social sign-in client with an ID but no secret.

| Setting | |
|---|---|
| `PROSENTRIQ_ENV` | `production` |
| `PROSENTRIQ_DATABASE_URL` | The application role (`prosentriq_app`). Never the owner role |
| `PROSENTRIQ_MIGRATION_DATABASE_URL` | The owner role (`prosentriq_owner`), used only by migrations. Keep it away from the API where you can |
| `PROSENTRIQ_REDIS_URL` | `redis://:PASSWORD@host:6379/0`, or `rediss://` for TLS |
| `PROSENTRIQ_PUBLIC_API_URL` | The API's public URL; sensors use it |
| `PROSENTRIQ_CONSOLE_URL` | The console's public URL |
| `PROSENTRIQ_TRUSTED_PROXIES` | How many proxies in front append to `X-Forwarded-For` (1 for one load balancer). Only safe if nothing else can reach the API |
| `PROSENTRIQ_SECRET_KEYS` | Fernet keys, comma-separated, for encrypting stored credentials. The first encrypts; all decrypt. Generate one with `prosentriq gen-secret-key` |
| `PROSENTRIQ_SIGNER` and its key | See [Signing keys](signing-keys.md). A local key comes from `prosentriq gen-signing-key` |
| `PROSENTRIQ_SMTP_HOST`, `_PORT` (587), `_USER`, `_PASSWORD`, `_FROM`, `_STARTTLS` | Outgoing mail |
| `PROSENTRIQ_METRICS_TOKEN` | Bearer token for the API's `/metrics` |
| `PROSENTRIQ_METRICS_PORT` | Port for each worker's `/metrics` (internal only) |
| `PROSENTRIQ_LOG_FORMAT` | `json` for one JSON object per line |
| `PROSENTRIQ_MANAGEMENT_CIDRS` | Your management networks: never blocked, and still reachable from an isolated host |
| `PROSENTRIQ_EGRESS_ALLOW_PRIVATE` | `1` to let integrations reach private addresses (an internal SIEM, for example). Off by default |
| `PROSENTRIQ_TSA_URL` | Optional RFC 3161 timestamp authority for evidence packs |
| `PROSENTRIQ_AI_PROVIDER` | `none` (default), `anthropic`, `bedrock` or `vertex`, with `PROSENTRIQ_AI_MODEL`, `_AI_REGION` and `_AI_GCP_PROJECT` |
| `PROSENTRIQ_GOOGLE_CLIENT_ID`/`_SECRET`, `PROSENTRIQ_MICROSOFT_CLIENT_ID`/`_SECRET` | Optional: [social sign-in](social-sign-in.md) |
| `PROSENTRIQ_LEGAL_TERMS_URL`/`_VERSION`, `PROSENTRIQ_LEGAL_PRIVACY_URL`/`_VERSION` | The documents every console user must accept. Point them at your own. Raising a version makes everyone accept again |
| `PROSENTRIQ_IMMUNITY_*` | Your private Immunity Network and [federation](federation.md) |
| `PROSENTRIQ_INGEST_EVENTS_PER_MINUTE` | Per sensor or API key (default 30,000) |
| `PROSENTRIQ_DB_POOL_MAX` | Connections per API worker (default 20) |

## First start

1. Create the database roles with the role script from the deployment bundle:
   `prosentriq_owner` owns the tables and runs migrations; `prosentriq_app`
   serves traffic and is neither a superuser nor the owner, so row-level
   security always applies.
2. Run migrations once per release: `prosentriq migrate`.
3. Start the API, the workers and the scheduler.
4. Create the first owner:

   ```bash
   prosentriq create-owner --email you@example.com --org "Your Co" --plan enterprise
   ```

5. Sign in to the console, create an enrollment key, and install sensors with
   `--api-base https://<your API URL>`.

Check it: `GET /readyz` answers 200 when the database and Redis are reachable,
and `GET /v2/public/version` shows the version.

## Upgrades

Releases are backward compatible with the previous one: each migration works
while the previous release is still serving. Upgrade by running `prosentriq
migrate` with the new image, then rolling the API and workers. Each migration
statement waits at most 5 seconds for a lock and then rolls back; run it again
when the blocking query is gone.

Next: [Operating a control plane](operating.md).
