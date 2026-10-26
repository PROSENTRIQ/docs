# Security model

Prosentriq runs with kernel-level access on your hosts and can block traffic.
This page explains what it can do, what it cannot do, and how that is enforced.

## On your hosts

- **Observe-only until you decide.** A new host runs `prosentriq_observe.o`,
  whose only exit returns `XDP_PASS`. It has no blocklist lookup, no
  `XDP_DROP` and no redirect: it cannot drop a packet, whatever the control
  plane says. Enforcement needs a paid plan, the host switched to enforce, and
  the Autonomy Dial.
- **Fail-open.** If the engine crashes or stops, traffic passes.
  `sudo prosentriq-ctl kill-switch` detaches every XDP program at once.
- **Least privilege on Kubernetes.** The DaemonSet isn't `privileged`. It holds
  only `BPF`, `PERFMON`, `NET_ADMIN`, `SYS_ADMIN`, `SYS_RESOURCE`, `SYS_PTRACE`
  and `KILL`.
- **Authenticated local API.** The host dashboard API needs a per-install
  token on every route, never reflects CORS, and locks out repeated failures.
- **No shell-outs.** Helpers run programs by absolute path with argument
  vectors, never through a shell.
- **Signed updates only.** Packages come only from apt and dnf repositories
  whose signing-key fingerprint is pinned in the released installer. The
  updater refuses any other source.
- **Isolation that can be undone.** An isolated host keeps the control plane,
  loopback, established connections and DNS to its own resolvers, so it can
  always be released.
- **Threat Hub peering** between hosts runs only over TLS pinned to each
  other's certificate, and is off until you turn it on.

## What leaves your hosts

- Security events and findings, as described in the [event schema](../api/events.md).
  The engine scores locally and sends findings and summarised activity, not
  packets.
- **Never uploaded**: packet payloads, file contents or memory dumps.

## In the control plane

- **Isolation by the database.** Every organization's rows are protected by
  Postgres row-level security, enforced for the application's own database
  role. A query that forgets its filter returns nothing from other
  organizations.
- **Only hashes of credentials** are stored: API keys, sensor tokens,
  enrollment keys, sessions and links. Integration credentials are encrypted
  at rest and never shown again.
- **Accounts**: Argon2id passwords; TOTP with single-use recovery codes that
  can't be replayed even during an outage; OIDC single sign-on that never
  skips a member's own TOTP; roles (owner, admin, analyst, auditor).
- **Account recovery** always goes through an emailed, single-use confirmation
  link. Nothing rotates on request alone.
- **Re-authentication** is required to delete an account or an organization.
- **Tamper-evident audit log**, hash-chained per organization.
- **No access by default.** Prosentriq staff can't see your incidents, hosts or
  integrations unless an owner grants time-limited [support access](../guides/access.md#support-access),
  and every look is recorded in your audit log.
- **Safe integrations.** Destinations can't target private addresses on the
  hosted service, redirects are never followed, and a stored credential can't
  be redirected to a new address without being re-entered.
- **The AI assistant** is off by default. When an owner turns it on it receives
  one incident's reasons with IP addresses, hosts and users replaced by tokens,
  and it cannot take any action.

## Signatures you can check

- Releases, packages, images, the Helm chart and SBOMs: [Verifying releases](verifying-releases.md).
- Evidence packs and the Immunity Network feed: [Signatures](../api/signatures.md).

## Reporting a vulnerability

Email **security@prosentriq.com**, or use GitHub's private vulnerability
reporting on the affected repository. Please don't open a public issue. See
the [security policy](https://github.com/PROSENTRIQ/.github/blob/main/SECURITY.md),
[prosentriq.com/security](https://prosentriq.com/security) and
[security.txt](https://prosentriq.com/.well-known/security.txt).
