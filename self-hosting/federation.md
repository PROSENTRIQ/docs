# Immunity Network federation

Every control plane runs its own [Immunity Network](../concepts/immunity-network.md)
across its own organizations. The hosted service runs the global network. A
self-hosted control plane runs a private **hub**: for example for an MSP and
its customers, a group of companies, or an air-gapped site.

Federation connects a self-hosted hub (the **peer**) to another hub, usually
the global network, in two independent ways. The hub's operator grants each
one separately:

| | What the peer gets or gives | Needs |
|---|---|---|
| **Consume** | The hub's signed feed, used next to the peer's own network | A peer token |
| **Contribute** | The peer's first-hand reports, counted on the hub as one reporter | A peer token and a signed contribution agreement |

To federate with the global network, contact sales@prosentriq.com.

## Safeguards

- **One peer, one reporter.** A peer counts once toward the hub's
  confirmations, however many organizations it serves. It is weighted like an
  organization: each indicator it withdraws costs 30% of its weight, and a
  contribution earns back at most 0.02. Below a weight of 0.25 its reports stop
  counting.
- **Peers never publish alone.** Peers together fill at most k − 1 of the k
  confirmations an indicator needs. At least one of the hub's own
  organizations must confirm, and the hub's never-block list is applied last
  as always.
- **First-hand only.** A peer contributes only what its own organizations
  observed, under the same eligibility rules (organization age, verified owner,
  reporter weight, owner domain). Indicators it received from a hub, and hits
  on them (`IMMUNITY_FEDERATED_HIT`), are never reported, so no verdict can
  amplify itself.
- **Authenticated, signed, fresh.** Contributions carry a `psqf_` token (only
  its SHA-256 is stored) and an Ed25519 signature by the peer's own signing
  key, which the hub pinned when it registered the peer. Each contribution is
  valid for an hour and must be newer than the last one applied, so replays
  and rollbacks are refused. A contribution holds at most 50,000 indicators,
  the body limit applies after decompression, and requests are rate-limited
  per peer and per address.
- **Verified feed.** A peer verifies the hub's feed against keys its own
  operator pinned (`PROSENTRIQ_IMMUNITY_UPSTREAM_PUBLIC_KEYS`), never against
  the key the feed carries. It refuses expired, future-dated, older and
  oversized feeds. Every entry is re-validated (a globally routable address,
  known reason categories, confidence) and must pass the peer's own
  never-block list. Expiry is capped at the peer's TTL and never extended as it
  passes from hub to hub.
- **Privacy.** Only addresses and reason categories cross, never events,
  hostnames or which organization reported.
- **Revocable.** Revoking a peer stops its token at once and withdraws all its
  reports, which are recomputed immediately.

## On the hub

```bash
# The peer's operator runs `prosentriq signing-key` and sends you the public key.
prosentriq federation add-peer --name acme-msp --public-key <base64> \
    --contribute --agreement "CA-2026-014"            # leave out both flags for consume-only
# -> PROSENTRIQ_IMMUNITY_UPSTREAM_TOKEN=psqf_…   (shown once: send it over a secure channel)

prosentriq federation list                            # weight, reports, last feed and contribution
prosentriq federation update --name acme-msp --no-contribute     # or --weight 1, or --public-key <new>
prosentriq federation revoke --name acme-msp
```

Also send the peer your signing key (`GET /v2/public/signing-key`, or
`prosentriq signing-key`). The peer must check it out of band.

## On the peer

```bash
PROSENTRIQ_IMMUNITY_UPSTREAM_URL=https://api.prosentriq.com
PROSENTRIQ_IMMUNITY_UPSTREAM_TOKEN_FILE=/etc/prosentriq-platform/upstream.token
PROSENTRIQ_IMMUNITY_UPSTREAM_PUBLIC_KEYS=<the hub's key; comma-separate several during a rotation>
PROSENTRIQ_IMMUNITY_UPSTREAM_CONTRIBUTE=1              # only with a contribution agreement
# Optional: PROSENTRIQ_IMMUNITY_UPSTREAM_SYNC_SECONDS (900), PROSENTRIQ_IMMUNITY_UPSTREAM_MAX_INDICATORS (250000)
```

The scheduler syncs the feed, then contributes, every
`PROSENTRIQ_IMMUNITY_UPSTREAM_SYNC_SECONDS`. To run it now and see the state:

```bash
prosentriq federation sync
prosentriq federation status
```

The hub's indicators go into the peer's own signed feed for its sensors,
marked `"source": "federated"`. A hit on one gives the reason
`IMMUNITY_FEDERATED_HIT`, which is low-risk: each organization's Autonomy Dial
still decides, as for any known-bad source (enforced from level 3, after the
blast-radius check).

If the hub changes its signing key and endorses the new one, the peer follows
the endorsement chain from a pinned key on its own. An unendorsed key is
refused, and the error shows in `federation status`.

## Network

The peer makes outbound HTTPS requests to the hub only:
`GET /v2/federation/feed`, `POST /v2/federation/contributions`, and
`GET /v2/public/signing-key` (only when the hub's key changes). The hub needs
nothing new inbound beyond its public API.

## Tuning

| Setting (on the hub) | Default | |
|---|---|---|
| `PROSENTRIQ_IMMUNITY_K` | 3 | Independent confirmations an indicator needs |
| `PROSENTRIQ_IMMUNITY_TTL_HOURS` | 72 | Lifetime of a published indicator |
| `PROSENTRIQ_IMMUNITY_MIN_REPORTER_AGE_DAYS` | 14 | How old an organization must be before its reports count |
| `PROSENTRIQ_IMMUNITY_FEDERATION_MAX_PEER_REPORTERS` | k − 1 | How many of the confirmations peers may fill |
