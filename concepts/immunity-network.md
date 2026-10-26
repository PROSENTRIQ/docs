# Collective Immunity Network

When enough Prosentriq customers independently see the same attacker, every
customer can block it before it reaches them. Only addresses are shared, never
traffic, and the network is built so that it cannot be turned against you.

## How an address gets published

1. When an organization sees a high-severity attacker, it reports the
   address and a reason family (for example `credential_access`).
2. The address is published to the shared feed only when **3 independent
   organizations** report it within the window.
3. Each published address has a TTL (72 hours by default) and expires unless
   it keeps being reported.
4. Sensors receive the feed on their heartbeat. A hit on a published address
   gives the reason `IMMUNITY_NETWORK_HIT`, which is low-risk: your
   [Autonomy Dial](autonomy.md) may enforce it from level 3, after the
   blast-radius check.

## Defences against poisoning

- **Independent reporters only.** A report counts only from an organization
  at least 14 days old with an email-verified owner. Reporters are counted by
  distinct owner email domain, and an MSP's customers count as the MSP, so a
  handful of throwaway sign-ups cannot get an address blocked everywhere.
- **Reporter weights.** A reporter whose blocks get undone loses weight, and
  its reports count for less.
- **Never-block list last.** Major DNS resolvers, cloud and CDN ranges, the
  Prosentriq control plane and non-routable ranges are filtered out after
  everything else. No number of reports can get them published.
- **Signed feed.** The feed is signed with the control plane's Ed25519 key.
  Sensors verify it against the key they pinned at enrollment before using it
  ([Signatures](../api/signatures.md)).

## Privacy

Only IP addresses and a reason family cross between organizations. Events,
hostnames, and which organizations reported an address are never shared.

## Opting out of contributing

Contributing is on by default. To stop sharing your organization's reports,
an owner turns off **Settings → Organization → Data sharing and AI → Contribute to the
Collective Immunity Network** (or `PATCH /v2/tenant` with `immunity_contribute: false`).
Your sensors keep receiving the feed.

## Live counters

[prosentriq.com/immunity](https://prosentriq.com/immunity) shows the network's
live counters, also served at `GET /v2/public/immunity`.

## Private hubs and federation (Enterprise)

A self-hosted control plane runs its own private network across its own
organizations, for example an MSP and its customers, or an air-gapped site.
It can also consume the global feed and, under a contribution agreement,
contribute to it as a single reporter. See [Federation](../self-hosting/federation.md).
