# Plans and billing

Prosentriq is priced per **enforcing node** per month, in US dollars. An
enforcing node is a host whose sensor runs in enforce mode. Observe-only hosts,
log relays and cloud collectors are never billed, on any plan. Billing counts
enforcing hosts daily.

The live prices are always on [prosentriq.com/pricing](https://prosentriq.com/pricing),
and the API serves them at `GET /v2/public/pricing`. This page describes
pricing version **2026-11**.

## Plans

| | Free | Starter | Pro | Enterprise |
|---|---|---|---|---|
| Price per enforcing node | $0 | $19 per month, or $228 per year | $49 per month, or $588 per year (volume tiers below) | Annual only, from 100 nodes: $468 per node per year |
| Nodes | Up to 5 hosts, observe-only | Up to 25 enforcing nodes | No limit | From 100 nodes, no limit |
| Enforcement | No (observe-only probe) | Yes | Yes | Yes |
| Highest autonomy level | 1 (Observe) | 3 (Enforce low-risk) | 5 (Full autonomy) | 5 (Full autonomy) |
| Data retention | 14 days | 30 days | 90 days | 400 days |
| Free trial | Free forever, no card | None | 7 days, once | By arrangement |
| Support | In-console cases, answered on business days as soon as we can | In-console cases and email, first response by the next business day | In-console chat and email, first response within 4 business hours | 24/7 for urgent cases with a 1-hour first response, 4 business hours for the rest, and a named contact |

Business hours are Monday to Friday, 09:00 to 18:00 East Africa Time (UTC+3),
except Kenyan public holidays. See [Getting help](guides/support.md).

Who each plan is for:

- **Free**: evaluating Prosentriq on real hosts, with no risk and no card. You
  see what it would block before it blocks anything.
- **Starter**: small teams protecting their first production fleet, often for
  an insurer or a first customer's security review.
- **Pro**: growing SaaS, fintech and health teams that answer to auditors, a
  SIEM and an on-call rotation.
- **Enterprise**: regulated, large or air-gapped estates with procurement,
  legal and uptime requirements.

## What each plan includes

| Feature | Free | Starter | Pro | Enterprise |
|---|---|---|---|---|
| Alerts to Slack, Microsoft Teams and signed webhooks | ✓ | ✓ | ✓ | ✓ |
| Trial Value Report (what would have been blocked, and why) | ✓ | | | |
| Single sign-on (OIDC) with verified domains | | ✓ | ✓ | ✓ |
| Signed SOC 2 evidence pack and cyber-insurance pack | | ✓ | ✓ | ✓ |
| PagerDuty, Opsgenie, syslog, Splunk, Elastic, Sentinel, Jira, ServiceNow and OpenTelemetry | | | ✓ | ✓ |
| Inbound SOAR response actions (signed) | | | ✓ | ✓ |
| Every framework (PCI DSS, HIPAA, ISO 27001, NIST CSF and 800-53, CIS v8, NIS2, DORA) | | | ✓ | ✓ |
| Auditor portal with time-boxed links | | | ✓ | ✓ |
| Honeytokens (fake credentials that call home when used) | | | ✓ | ✓ |
| Sigma and Falco rule import | | | ✓ | ✓ |
| Side-by-side displacement report against your current tool | | | ✓ | ✓ |
| AI investigation assistant (optional, redacted context) | | | ✓ | ✓ |
| Self-hosted and air-gapped control plane, federation | | | | ✓ |
| Annual invoicing, DPA and security questionnaire support | | | | ✓ |

The Trial Value Report is only on Free. Paying organizations see the real
decision ledger instead.

**Included in every plan, Free included:**

- XDP kernel-level enforcement with fail-open behaviour (paid plans). On Free,
  an observe-only probe that cannot drop a packet.
- Autonomy Dial with counterfactual ledger, blast-radius checks, canary
  rollouts, circuit breaker and one-click undo
- Explainable detections with MITRE ATT&CK mapping and incident storylines
- Ransomware tripwires (canary files, mass-modification and entropy-burst detection)
- TOTP MFA, roles and a tamper-evident audit log
- Collective Immunity Network
- Migration kit (allow-list import and export)

## Volume tiers

Pro and Enterprise get volume pricing automatically. The rate is set by your
fleet size and applies to every enforcing node. Starter is one flat price; it
stops at 25 enforcing nodes, below the first break.

| Enforcing nodes | Per node per month | Per node per year |
|---|---|---|
| 1 – 99 | $49 | $588 |
| 100 – 999 | $39 | $468 |
| 1,000 and more | $29 | $348 |

For example, 150 enforcing nodes on Pro cost 150 × $39 = $5,850 per month.

## Annual billing

Annual billing is twelve months' price, paid up front. There is no separate
annual discount. Enterprise is annual only.

## Free trials

- **Free** never expires and needs no card.
- **Pro** starts with a 7-day free trial, once per organization and once per
  paying customer. Checkout takes a card but charges nothing until day 8.
  Cancel before then and you pay nothing.
- **Starter** has no trial. Start on Free to see what it would block first.

## Managed service providers

MSPs pay list price minus **35%** for every customer node they manage on
Starter or Pro. Wholesale is billed monthly, and checkout applies it on its own.

| Plan and fleet size | List | MSP wholesale |
|---|---|---|
| Starter | $19 | $12.35 |
| Pro, 1 – 99 nodes | $49 | $31.85 |
| Pro, 100 – 999 nodes | $39 | $25.35 |
| Pro, 1,000 nodes and more | $29 | $18.85 |

Customer organizations an MSP creates start on Free. Only the MSP's owner pays
for them. See [Managed service providers](guides/msp.md).

## Changing plans

Only an organization's owner can change its plan. Do it at any time from the
console's **Plans** page (Settings → Usage & migration → See plans). Upgrades
take effect immediately.

Nothing is deleted on a downgrade. Instead:

- Capabilities the new plan doesn't include pause. For example, a SIEM
  destination keeps its settings but stops receiving, and SSO, auditor links,
  honeytokens and imported rules pause.
- The autonomy level is lowered to the new plan's highest level.
- On Starter, the 25 longest-enrolled enforcing nodes keep enforcing and the
  rest observe.
- Your previous, longer data retention is kept for 30 days, so you can change
  your mind.

When you call an API feature your plan doesn't include, the API answers
`402 plan_feature` and names the cheapest plan that does
(see [API errors](api/README.md#errors)).

## If you stop paying

After a grace period your organization moves to Free. You get an email first.
Enforcement is suspended (hosts go back to observe) and nothing is deleted.
The [Terms of Service](https://prosentriq.com/legal/terms#billing) have the details.

## Payments and invoices

Payments are processed by Paddle, our merchant of record. Paddle handles sales
tax and VAT and issues your invoices. The person who subscribed manages the
payment method, invoices and cancellation in Paddle's billing portal:
**Settings → Usage & migration → Manage billing**. Enterprise is
invoiced annually; contact sales@prosentriq.com.
