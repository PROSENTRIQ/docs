# Troubleshooting and FAQ

## Linux sensor

**The installer says the enrollment key is invalid.** Keys expire (30 days by
default) and can be limited in uses. Create a new one on **Sensors**. Check
you pasted the whole `psqe_…` value.

**The installer can't reach the control plane or the repository.** The host
needs outbound HTTPS to `api.prosentriq.com` (or your `--api-base`) and
`packages.prosentriq.com` (or your `--repo-url`). Behind a proxy, export
`https_proxy` before running it. Run with `--dry-run` to check everything
without changing the host.

**The host doesn't appear on Sensors, or shows as stale.**

```bash
sudo prosentriq-ctl status
systemctl status prosentriq-bridge prosentriq-loader prosentriq-ai
journalctl -u prosentriq-bridge --since "15 min ago"
```

A heartbeat is sent every 30 seconds. A clock more than 10 minutes off makes
events be rejected: check that NTP is running.

**XDP won't attach.** The kernel must be 5.4 or later. Check the interface with
`ip link` and pass `--iface`. Some virtual NICs only support generic XDP, which
works but is slower.

**The process profiler reports nothing.** It needs BTF at
`/sys/kernel/btf/vmlinux`. Most current distribution kernels have it.

**I set a host to enforce but nothing is blocked.** Check, on the Autonomy dial
page, what the effective level is and what holds it down: Free is observe-only,
Starter stops at level 3, a host cap or an open circuit breaker lowers it.
At level 1 or 2 nothing is enforced automatically by design. The Decision
ledger shows what would have happened and why.

**Something is blocked that shouldn't be.** **Undo** the action (Approvals &
actions). Add the address to the allowlist so it is never blocked again. If
you need traffic untouched right now: `sudo prosentriq-ctl kill-switch`.

## Kubernetes

**Pods crash-loop.** The node needs BTF (`/sys/kernel/btf`) and the chart's
capabilities. Check `interface` matches the node's interface name (`eth0`,
`ens5`, …). `kubectl -n prosentriq logs ds/prosentriq-agent` shows the cause.

## Events and the API

**`400 all_rejected` or entries in `errors`.** Each error names the field. The
usual causes are a missing `metadata.uid` or `prosentriq.host_id`, or a `time`
outside the accepted window (10 minutes ahead, 30 days back).

**`401 invalid_credentials`.** The key was revoked or the sensor retired, or
the token is incomplete.

**`402 plan_feature`.** The feature isn't on your plan; `detail.required_plan`
says which plan has it.

**`403 forbidden`.** The API key lacks a scope, or your role a permission. The
message names it.

**`429`.** Wait for `Retry-After` seconds. The SDK does this for you.

## Integrations

**Send test works but real alerts don't arrive.** Check the destination's
minimum severity (default `medium`) and event types. Incident updates, undos,
breaker resets and rollout events are off by default.

**Deliveries end in Dead letters.** The error is shown with each one. A `400`
or `401` from the receiver isn't retried: fix the credential or URL, then
retry. Private addresses are refused on the hosted service.

**Webhook signatures don't verify.** Verify against the raw body bytes before
any JSON parsing, and check your server's clock (5-minute window). See
[Signatures](api/signatures.md).

## Accounts

**Lost authenticator.** Sign in with one of your recovery codes, then set up
the authenticator again (Settings → My security). If you've lost the recovery
codes too, contact support@prosentriq.com.

**"Access blocked" or "needs admin approval" with Google or Microsoft.** Your
Workspace or Entra administrator must allow the Prosentriq app once for your
organization.

**An invitation says the address belongs to another organization.** An account
belongs to one organization. Ask an admin of the other organization to remove
you first, or use a different address.

## FAQ

**Does Prosentriq replace my EDR?** For Linux servers and Kubernetes it
covers network enforcement, behavioural detection, file integrity, deception
and response. Run it next to your current tool and compare with the
[displacement report](guides/evaluation.md). Windows and macOS sensors are not
available yet.

**Will it block my own infrastructure?** The blast-radius check refuses to
block your allowlist, public DNS resolvers, major cloud and CDN ranges, the
control plane, a host's own address and gateway, and anything wider than a
/24 or /48. Private ranges and established peers need a person's approval.

**What happens if the control plane is unreachable?** Hosts keep enforcing what
they already have, with their local circuit breaker, and keep failing open.
Events are buffered and sent when the connection returns.

**Is my data used to train AI?** No. The optional AI assistant is off by
default and receives only a redacted summary of one incident when you ask.

**Where can I see the code?** The Sensor SDK and event schema are open source
(Apache-2.0), and the Helm chart's source is public. The control plane and
engine are commercial; Enterprise customers can self-host them.

Still stuck? support@prosentriq.com, with the `request_id` from any API error.
