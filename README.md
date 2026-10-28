<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/PROSENTRIQ/.github/main/profile/logo-lockup.svg">
    <img src="https://raw.githubusercontent.com/PROSENTRIQ/.github/main/profile/logo-lockup-light.svg" alt="Prosentriq" width="260">
  </picture>
</p>

# Prosentriq documentation

Prosentriq protects Linux hosts and networks on its own, and you can prove it
is safe before it blocks anything. It also generates your audit evidence. It
is one control plane plus thin, replaceable sensors. Every detection is
explained, every decision is recorded whether or not it was enforced, and
enforcement is turned up one step at a time through the Autonomy Dial.

This is the full public reference. A shorter overview is at
[prosentriq.com/docs](https://prosentriq.com/docs).

## Start here

- [Getting started](getting-started.md): from sign-up to your first finding in about 10 minutes
- [Plans and billing](plans-and-billing.md): Free, Starter, Pro and Enterprise, what counts as a node, trials, changing plans

## Install sensors

| Where | Guide |
|---|---|
| Linux hosts (Debian/Ubuntu, RHEL/Alma/Rocky, Fedora, Amazon Linux 2023; x86_64 and ARM64) | [install/linux.md](install/linux.md) |
| Kubernetes (DaemonSet with pod, namespace and image attribution) | [install/kubernetes.md](install/kubernetes.md) |
| Firewalls, IDS, sshd and your current EDR (syslog, CEF, Suricata EVE) | [install/log-sources.md](install/log-sources.md) |
| AWS, agentless (VPC Flow Logs, CloudTrail) | [install/aws.md](install/aws.md) |
| Your own sensor (Python SDK or plain HTTP) | [install/custom-sensor.md](install/custom-sensor.md) |

## Concepts

- [Architecture](architecture/ARCHITECTURE.md): how sensors and the control plane fit together
- [The Autonomy Dial and its safety mechanisms](concepts/autonomy.md)
- [Detections, incidents and storylines](concepts/detections.md)
- [Collective Immunity Network](concepts/immunity-network.md)

## Guides

- [Using the console](guides/console.md): a tour of each page
- [Rules: Sigma, Falco and canary rollouts](guides/rules.md)
- [Honeytokens and ransomware tripwires](guides/honeytokens.md)
- [Integrations: Slack, Teams, PagerDuty, SIEMs, webhooks](guides/integrations.md)
- [SOAR response actions](guides/soar.md)
- [Compliance evidence and the auditor portal](guides/compliance.md)
- [Teams, roles, API keys, MFA and single sign-on](guides/access.md)
- [Managed service providers](guides/msp.md)
- [Side-by-side evaluation and migration](guides/evaluation.md)
- [On the host: `prosentriq-ctl`, kill-switch, isolation, upgrades](guides/host.md)
- [Your data: retention, export and deletion](guides/data.md)
- [Getting help: support cases, response times and data access](guides/support.md)

## API

- [API overview](api/README.md): authentication, errors, limits, permissions, every route
- [Sending events](api/events.md): `POST /v2/events` and the event schema
- [Webhook and signature verification](api/signatures.md)
- [OpenAPI specification](api/openapi.json) (a snapshot; every control plane serves its own at `/v2/openapi.json`)
- The event JSON Schema: [prosentriq-sdk-python/schema](https://github.com/PROSENTRIQ/prosentriq-sdk-python/blob/main/schema/prosentriq-event.schema.json), also served at `GET /v2/public/schema`

## Enterprise: self-hosting

- [Self-hosting the control plane](self-hosting/README.md): topologies, requirements, configuration
- [Operating a control plane](self-hosting/operating.md): processes, database, health, metrics, routine tasks
- [Signing keys](self-hosting/signing-keys.md): local, AWS KMS, Google Cloud KMS, Vault; changing keys
- [Immunity Network federation](self-hosting/federation.md): private hubs and the global network
- [Social sign-in](self-hosting/social-sign-in.md): Continue with Google and Microsoft

## Trust

- [Security model](security/README.md): what Prosentriq can and cannot do on your hosts
- [Verifying releases](security/verifying-releases.md): Sigstore signatures, the package repository key and SBOMs
- [Troubleshooting and FAQ](troubleshooting.md)

## Other public repositories

| Repository | What it is |
|---|---|
| [prosentriq-sdk-python](https://github.com/PROSENTRIQ/prosentriq-sdk-python) | Python Sensor SDK and the open event schema (Apache-2.0) |
| [helm-charts](https://github.com/PROSENTRIQ/helm-charts) | Helm chart for the Kubernetes sensor |
| [releases](https://github.com/PROSENTRIQ/releases) | Signed installer, packages and SBOMs, and how to verify them |

## Help and contact

- Support: open a case in the console (Help → Contact support), or write to support@prosentriq.com. See [Getting help](guides/support.md).
- Sales and Enterprise: sales@prosentriq.com
- Security reports: security@prosentriq.com; see the [security policy](https://github.com/PROSENTRIQ/.github/blob/main/SECURITY.md). Please don't report vulnerabilities in public issues.

Found a mistake in these docs? Open an issue in this repository.

---

Prosentriq is made by Torcis Ltd. The control plane, console and sensor engine
are commercial software. These documents are © Torcis Ltd; you may copy the
code samples into your own scripts and configuration freely.
