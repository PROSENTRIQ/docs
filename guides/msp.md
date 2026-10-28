# Managed service providers

An MSP account manages many customer organizations from one place, at
wholesale prices, under its own brand.

## Get an MSP account

MSP accounts are set up by Prosentriq. Email sales@prosentriq.com, or see
[prosentriq.com/msp](https://prosentriq.com/msp).

## Customer organizations

Create customers in **Customer fleet** (`POST /v2/msp/tenants` with a `name`).
Owners and admins of the MSP can do it, from the console or with an API key.

- A customer organization starts on **Free**. To give it enforcement, subscribe
  it to Starter or Pro from its own Plans page. Your wholesale discount is
  applied at checkout, and only the MSP's owner pays.
- Each customer's data is isolated from every other customer's by the
  database itself (row-level security), as for any organization.
- Customers inherit your branding (product name, logo, colours, support email).
- You answer your customers' support cases first: they appear in **Support →
  Customers' cases**, and your support email (or your owners and admins) gets
  an email for each. Escalate one to Prosentriq when you need us; we then see
  that conversation and answer it on the customer's plan. See
  [Getting help](support.md#if-you-are-an-msp).

## Working in a customer organization

Switch with the organization selector in the console. Through the API, send
the customer's id in `X-Prosentriq-Tenant` ([API overview](../api/README.md#managed-service-providers)).

MSP members act in customer organizations with their MSP role, capped at
admin: ownership of a customer organization stays with the customer.

**Customer fleet** lists every customer, worst first: hosts and how many
enforce, open and critical incidents, open circuit breakers, the autonomy level
and when each was last seen. Open one to act in it.

## Wholesale pricing

MSPs pay list minus **35%** for every customer node on Starter or Pro, billed
monthly:

| Plan and fleet size | List | MSP wholesale |
|---|---|---|
| Starter | $19 | $12.35 |
| Pro, 1 – 99 nodes | $49 | $31.85 |
| Pro, 100 – 999 nodes | $39 | $25.35 |
| Pro, 1,000 nodes and more | $29 | $18.85 |

Wholesale is monthly only; checkout refuses annual billing for an MSP's
customer. See [Plans and billing](../plans-and-billing.md#managed-service-providers).

## A private Immunity hub (Enterprise)

On Enterprise, an MSP can self-host its control plane and run a private
Immunity Network across its customers, optionally federated with the global
network. See [Federation](../self-hosting/federation.md).

## Removing a customer

The MSP's owner deletes a customer organization from **Customer fleet**
(`POST /v2/msp/tenants/{id}/delete`, with re-authentication). Access stops at
once, and the data is purged after 30 days. Until then, support@prosentriq.com
can restore it.
