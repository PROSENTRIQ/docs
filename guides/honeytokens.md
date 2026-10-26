# Honeytokens and ransomware tripwires

## Honeytokens (Pro)

A honeytoken is a decoy credential or file that nobody legitimate ever uses.
When one is used, Prosentriq opens a **critical** incident with the reason
`HONEYTOKEN_TRIGGERED`. It is a low-risk reason, so from Autonomy level 3 the
source is blocked automatically.

Plant one from **Honeytokens → Plant a honeytoken**, or with
`POST /v2/honeytokens` (`kind`, `name`, and for a decoy file `sensor_id` and
`placement_path`). The artifact is shown **once**.

| Kind | What you get | Where to plant it |
|---|---|---|
| `aws_credentials` | An AWS shared-credentials profile with a decoy access key. Its config points the endpoint at Prosentriq, so an attacker's first AWS CLI or SDK call calls home | `~/.aws/credentials` on servers, CI runners, developer laptops |
| `canary_url` | A unique URL | Wikis, bookmarks, config comments, internal documents |
| `env_file` | A `.env` file with decoy secrets and a callback URL | Application directories and repositories |
| `decoy_file` | Any file on one host, watched by that host's sensor. Every read is reported | Anywhere an intruder would look, for example `/root/backup-keys.txt` |

The callback never reveals that it is a trap. AWS-style calls get an
AWS-shaped authentication error and everything else gets a plain 404.

Revoke a honeytoken when you remove it (`DELETE /v2/honeytokens/{id}`). If your
plan stops including honeytokens, they pause and resume after an upgrade.

Integrations receive `honeytoken.triggered`.

## Ransomware tripwires (every plan)

Two correlators watch file activity on Linux sensors:

- **Canary files.** Any change to a file matching the canary patterns gives
  `RANSOMWARE_TRIPWIRE` (score 500). The default patterns are
  `*.prosentriq-canary*`, `*_prosentriq_canary_*` and `~$prosentriq-canary*`.
  Create such files in the directories you care about, for example
  `/srv/share/~$prosentriq-canary.docx`.
- **Mass modification.** One process modifying 100 or more files on a host
  within 60 seconds gives `MASS_FILE_MODIFICATION` (score 200). The reason
  reports the files' average entropy, since encrypted output is a strong sign
  of ransomware.

At Autonomy level 5 the response can include freezing the offending process,
which can be thawed with one click.

Change the patterns or the threshold with `PATCH /v2/tenant`:

```json
{ "ransomware": { "canary_globs": ["*.canary", "~$budget-final*.xlsx"], "mass_threshold": 200 } }
```

Patterns are matched against the file's name, not its directory. Each is 1–200
characters and must name something besides wildcards (at most 50 patterns).
Setting `canary_globs` replaces the defaults.
