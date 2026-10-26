# Rules: Sigma, Falco and canary rollouts

Prosentriq ships built-in detections (the [reason catalog](../concepts/detections.md#reasons)).
On top of them you can add your own rules: imported from Sigma or Falco (Pro),
or written by hand. Every rule compiles to one internal form and is evaluated
against every event your sensors send.

## Import Sigma or Falco rules (Pro)

**Rules → Import rules**, paste the YAML, and choose what a match does:

- `alert`: a detection with the rule's score (default)
- `block_ip`: also propose blocking the source. The [Autonomy Dial](../concepts/autonomy.md)
  still decides.

Or with the API:

```bash
curl -X POST https://api.prosentriq.com/v2/rules/import \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile c rules.yml '{format:"sigma", content:$c, action:"alert"}')"
```

**What is supported.**

- *Sigma*: map and list-of-map selections, keyword lists, the `contains`,
  `startswith`, `endswith`, `re`, `cidr`, `all`, `gt`, `gte`, `lt`, `lte`
  and `exists` modifiers, wildcards, null checks, and the full condition
  grammar including `1 of` and `all of` patterns and `them`.
- *Falco*: `- rule`, `- macro` and `- list` items, the boolean grammar,
  `= != < <= > >= in contains icontains startswith endswith glob pmatch exists`,
  macros and lists defined in the same file plus Falco's common default macros,
  and the process, user, file, network, container and Kubernetes fields
  Prosentriq's sensors populate.

**What is rejected.** Anything that can't be evaluated faithfully is rejected
with the reason, never imported in a weakened form. That includes Sigma
aggregations, the `base64` and `utf16` modifiers, `fieldref`, and fields with
no mapping to the event schema. A rule that silently matches less than its
author intended is worse than no rule.

Imported rules start as **drafts**. They match nothing until you roll them out.

## Write a custom rule

`POST /v2/rules` with a name, a severity (`low`, `medium`, `high`, `critical`),
a score (0–1,000, default 50), ATT&CK technique ids, an action and the rule
itself in `compiled`:

```json
{
  "name": "Download-and-execute from a shell",
  "severity": "high",
  "score": 120,
  "attack": ["T1059"],
  "action": "alert",
  "compiled": {
    "classes": [1007],
    "selections": {
      "sel":    [ { "field": "process.cmd_line", "op": "contains", "values": ["curl", "wget"], "nocase": true } ],
      "pipe":   [ { "field": "process.cmd_line", "op": "contains", "values": ["| sh", "| bash"] } ],
      "filter": [ { "field": "actor.user.name", "op": "eq", "values": ["ansible"] } ]
    },
    "condition": { "op": "and", "args": [ { "sel": "sel" }, { "sel": "pipe" }, { "op": "not", "arg": { "sel": "filter" } } ] }
  }
}
```

- `classes` limits the rule to OCSF event classes (optional).
- A selection is a list of predicates that must **all** hold. A predicate holds
  if **any** of its `values` matches, or all of them with `"all": true`.
  `"nocase": true` ignores case.
- Operators: `eq`, `contains`, `startswith`, `endswith`, `glob`, `re`
  (linear-time regular expressions), `cidr`, `gt`, `gte`, `lt`, `lte`,
  `exists` and `null`.
- Fields are dotted paths into the event, as in the [event schema](../api/events.md).
- `condition` combines selections with `and`, `or` and `not`.

Test a rule against recent events before rolling it out: `POST /v2/rules/test`.

## Roll it out

**Rules → the rule → Start canary** (`POST /v2/rules/{id}/rollout`, with an
optional `dwell_seconds` between 60 seconds and 7 days, default 1 hour):

| Stage | Where the rule runs |
|---|---|
| 1 | One host, observe-only. Matches are recorded, nothing is enforced |
| 2 | About 10% of hosts, enforcing |
| 3 | Every host, enforcing. The rule is then **active** |

A stage advances after its dwell time only if no undo or false positive is
attributed to the rule, no circuit breaker is open, and its match rate is
normal. Otherwise the rollout rolls back on its own and reverts every action
the rule caused. Integrations receive `rollout.advanced` and
`rollout.rolled_back`. An active rule that collects 3 undos within 24 hours is
rolled back too.

Roll back by hand at any time: `POST /v2/rules/{id}/rollback`. Disable a rule
with `PATCH /v2/rules/{id}` and `{"status": "disabled"}`.

## Machine-generated suggestions

Prosentriq can also propose rules from the attacks it has seen
(`POST /v2/rules/evolve`). They are drafts like any other rule, and go through
the same canary rollout.

## On a downgrade

If your plan no longer includes rule import, imported rules pause. They keep
their settings and resume when you upgrade.
