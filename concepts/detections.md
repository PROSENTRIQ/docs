# Detections, incidents and storylines

Prosentriq never shows a bare score. Every point an attacker's score gains
comes with a **reason**: a sentence, the events that prove it, and the MITRE
ATT&CK techniques it maps to.

## From events to incidents

1. Sensors send events ([Sending events](../api/events.md)).
2. The detection pipeline scores each event against the reason catalog below,
   your rules (built-in, Sigma, Falco, custom), stateful correlators (credential
   chains, ransomware bursts, egress baselines, honeytokens) and context (the
   Immunity Network, threat feeds).
3. Each match is a **detection** on an **actor**: usually a source address, or
   a host for process and file activity.
4. Detections on the same actor within 24 hours group into one **incident**.
5. The incident's score crosses a tier, and the [Autonomy Dial](autonomy.md)
   decides what to do.

## Scoring

An actor's score is the sum of its reasons, plus a correlation bonus for
sustained activity: `min(events × 10 × days, 150)`. Scores decay over time
(×0.98), more slowly for actors that keep coming back.

| Tier | Score |
|---|---|
| Medium | 100 |
| High | 200 |
| Critical | 350 |

These constants are the same on the host engine and in the control plane, so a
host and the cloud agree on what an event is worth. Scores are kept per
organization.

## Reasons

| Code | Score | ATT&CK | Low-risk¹ | Sentence |
|---|---|---|---|---|
| `SUSPICIOUS_ENTROPY_PACKET` | 25 | T1001, T1573 | | High-entropy payload on a non-standard port, typical of packed or encrypted command-and-control |
| `HIGH_RISK_GEOIP` | 10 | | | Source geolocates to a configured high-risk country |
| `THREAT_INTEL_HIT` | 100 | | ✓ | Source address is listed on a live threat-intelligence feed |
| `PORT_SCAN_DETECTED` | 50 | T1046, T1595 | | Contacted many distinct ports within 10 seconds |
| `PROTOCOL_MISMATCH_SSH` | 150 | T1571 | | SSH handshake on a non-standard port |
| `PROTOCOL_MISMATCH_HTTP` | 100 | T1571 | | Plain HTTP on a non-HTTP port |
| `PROTOCOL_MISMATCH_TLS` | 100 | T1571, T1573 | | TLS handshake on a non-standard port |
| `SSL_BAD_JA3` | 50 | T1071.001 | | TLS client fingerprint (JA3) matches known malware tooling |
| `DNS_SUSPICIOUS_TLD` | 5 | T1071.004 | | DNS lookup under a frequently abused top-level domain |
| `DNS_HIGH_ENTROPY_DGA` | 75 | T1568.002 | | DNS lookup looks algorithmically generated |
| `HONEYPOT_HIT` | 500 | T1595 | ✓ | Connected to a honeypot port; no legitimate client has a reason to |
| `BEHAVIORAL_VIOLATION` | 50 | T1071 | | A process connected outside its learned behaviour |
| `NETWORK_ANOMALY` | 75 | | | Traffic deviates from the host's learned network baseline |
| `FIM_CREATE` | 15 | T1565.001 | | Unexpected file created in a protected path |
| `FIM_MODIFY` | 20 | T1565.001 | | Protected file modified |
| `FIM_DELETE` | 25 | T1565.001 | | Protected system file deleted |
| `FIM_MOVE` | 40 | T1574 | | Protected binary moved or overwritten (possible hijack) |
| `FIM_ATTRIB` | 50 | T1222 | | Permissions elevated on a protected file |
| `FIM_CLOSE_WRITE` | 30 | T1565.001 | | New content written to a protected path; the artifact is quarantined |
| `AUTH_BRUTE_FORCE` | 50 | T1110.001 | | Many failed logins from one source (password guessing) |
| `AUTH_SUCCESS_AFTER_FAILURES` | 150 | T1110, T1078 | | Successful login after failures from the same source |
| `CREDENTIAL_ATTACK_CHAIN` | 200 | T1110, T1078, T1059 | | Brute force, then a login, then a new process: a complete intrusion chain |
| `HONEYTOKEN_TRIGGERED` | 500 | T1552.001 | ✓ | A planted decoy credential was used; only an intruder holds it |
| `RANSOMWARE_TRIPWIRE` | 500 | T1486 | | A canary file was modified |
| `MASS_FILE_MODIFICATION` | 200 | T1486 | | One process modified many files within a minute (with their average entropy): a ransomware-like burst |
| `EGRESS_VOLUME_ANOMALY` | 100 | T1048 | | A process sent far more data than its baseline |
| `IMMUNITY_NETWORK_HIT` | 100 | | ✓ | Independently reported as malicious by other Prosentriq customers |
| `IMMUNITY_FEDERATED_HIT` | 100 | | ✓ | Reported across the federated Immunity Network |
| `RULE_MATCH` | 50² | | | Matched one of your rules |
| `INCUMBENT_ALERT` | 0 | | | An alert from your current tool, in side-by-side mode (not scored) |

¹ Low-risk reasons are known-bad with near-zero false positives. They are what
Autonomy level 3 may act on by itself.
² A rule can set its own score.

A sensor can report a reason it has already recognised by sending its code as
`prosentriq.signal` on an event.

## Incidents

Each incident has a severity (from its score tier), a status and a storyline.

| Status | Meaning |
|---|---|
| `open` | New, or active again |
| `acknowledged` | Someone is on it |
| `resolved` | Dealt with |
| `false_positive` | It wasn't an attack. To also reverse what was enforced, and count it against the rule and the circuit breaker, **Undo** the incident's actions |

Change the status on the incident page or with `PATCH /v2/incidents/{id}`.
Integrations receive `incident.opened`, `incident.escalated` (a higher tier)
and `incident.updated`.

## The storyline

**Incidents → an incident → Storyline** (`GET /v2/incidents/{id}/storyline`)
merges, in time order, everything about the actor: its events, each detection
with its reasons and evidence, each decision with its safety checks, and each
action with its undo. It is meant to be read by a person, and it's the record
an auditor sees.

## The AI investigation assistant

On Pro and Enterprise an owner can turn on the AI investigation assistant
(**Settings → Organization → Data sharing and AI → Investigation assistant (AI)**). It is off by default. It answers questions about
an incident from a redacted summary of it, and it cannot take any action.
