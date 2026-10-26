# Side-by-side evaluation and migration

## Evaluate on Free first

Every host starts observe-only, so you can run Prosentriq next to your current
tool on production hosts with no risk. After 7 days the **Trial Value Report**
(Free plan) sums up what Prosentriq would have blocked, why, and that none of
it touched your allowlist. Preview it at any time in **Reports**.

## The displacement report (Pro)

To compare Prosentriq with the tool you use today (EDR, NDR or SIEM), send that
tool's alerts to Prosentriq. They are kept apart and never scored.

- **From syslog or CEF**: run the [log relay](../install/log-sources.md#side-by-side-with-your-current-tool)
  with `--incumbent VENDOR`.
- **From anything else**: `POST /v2/displacement/alerts` with an API key that
  has the `ingest` scope:

```json
{
  "vendor": "acme-edr",
  "alerts": [
    { "uid": "alert-99812", "time": "2026-10-26T09:12:00Z", "indicator": "185.220.101.4",
      "title": "Suspicious SSH logins", "severity": "high", "raw": { } }
  ]
}
```

Up to 1,000 alerts per request; `uid` makes retries free. `indicator` is an IP
address or a host name, and `severity` is `low`, `medium` (default), `high` or
`critical`.

Then generate the report in **Reports**, or with
`POST /v2/displacement/report?days=14` (1 to 90 days). It shows:

| Section | |
|---|---|
| Caught by both | Attackers both tools saw |
| Only Prosentriq (what they missed) | Attackers only Prosentriq caught |
| Only the incumbent (what we missed) | Attackers only your current tool caught |
| Prosentriq first | Where both caught it, how often Prosentriq was first, and the median lead in minutes |

The report shows what Prosentriq missed as plainly as what it caught.

## Compare the price

The calculator on [prosentriq.com/pricing](https://prosentriq.com/pricing)
compares your current quote with Pro for your fleet size. `GET /v2/public/pricing/quote`
gives the same number from the API.

## Migration kit (every plan)

### Import an allowlist from another tool

**Settings → Usage & migration → Migration kit**, or `POST /v2/migrate/allowlist`:

```json
{ "format": "lines", "source": "old-firewall", "content": "10.0.0.0/8   # office\n203.0.113.7  # partner VPN\n" }
```

`lines` takes one IP or CIDR per line, with `#` comments as notes. `csv` takes
a header row with a `cidr`, `ip`, `address` or `value` column, and optionally a
`note`, `comment` or `description` column. Invalid lines are returned as
rejected; everything else is added to your allowlist.

### Export and import your configuration

`GET /v2/migrate/export` returns a portable bundle (`prosentriq-config/1`):
your allowlist, rules, destinations (without their credentials), autonomy
level, settings and branding. `POST /v2/migrate/import` loads one into another
organization or another control plane, for example from hosted to
self-hosted. Imported rules arrive as drafts, and destination credentials must
be entered again.

There is no lock-in: the same bundle lets you leave.
