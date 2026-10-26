# Getting started

From sign-up to your first explained finding takes about 10 minutes. Nothing
Prosentriq installs can block traffic until you decide it should.

## 1. Create your organization

Sign up at [cockpit.prosentriq.com](https://cockpit.prosentriq.com/signup) with
an email and password, or with **Continue with Google** or **Continue with
Microsoft**. New organizations start on the **Free** plan: up to 5 hosts in
observe-only mode, no card and no time limit. See [Plans and billing](plans-and-billing.md).

Confirm your email, accept the Terms and Privacy Policy, and you land on the
**Welcome** checklist. It ticks itself off as you go.

Do this on day one: **Settings → My security → Set up two-factor
authentication** (TOTP). Keep the recovery codes it shows you somewhere safe.

## 2. Install a sensor on one or two hosts

Open **Sensors → Create enrollment key**. The console shows ready-to-paste
commands for each kind of sensor. On a Linux host:

```bash
curl -fsSL https://prosentriq.com/install.sh | sudo bash
```

The installer asks for the enrollment key with the input hidden. It checks the
key before it changes anything on the host. Then it installs the signed
package and starts the sensor in **observe** mode. No reboot is needed. Full
details and every flag: [install/linux.md](install/linux.md).

Other sensors: [Kubernetes](install/kubernetes.md), [log sources](install/log-sources.md),
[AWS](install/aws.md), [your own](install/custom-sensor.md).

## 3. Read what Prosentriq sees

Within minutes the host shows as fresh on **Sensors**, and **Overview** starts
counting events.

- **Incidents** groups detections by attacker (actor). Each incident's
  **Storyline** lists every reason that raised its score. A reason is a
  sentence, the evidence behind it and the MITRE ATT&CK technique.
- **Decision ledger** shows what Prosentriq *would* have done, and which safety
  checks ran. For example: "refused: 8.8.8.8 is a public DNS resolver".
- On day 7 the **Trial Value Report** arrives by email and in **Reports**. It
  sums up what would have been blocked, and why.

## 4. Decide when to enforce

When the ledger shows decisions you agree with, upgrade to Starter or Pro
(Pro starts with a 7-day trial). Then:

1. Switch the hosts you want protected to **enforce** (Sensors → the host → Mode).
2. Turn the **Autonomy dial** up one level at a time. Level 2 (Suggest) puts
   every action in **Approvals & actions** for a person to approve. Level 3
   enforces only known-bad sources automatically.

Every enforced action can be undone with one click. A circuit breaker drops the
organization back to Observe if blocks or undos spike. See
[The Autonomy Dial](concepts/autonomy.md).

## 5. Connect your tools

**Integrations → Add a destination** sends incidents and actions to Slack,
Microsoft Teams or a signed webhook on every plan. PagerDuty, Opsgenie, syslog,
Splunk, Elastic, Microsoft Sentinel, Jira, ServiceNow and OpenTelemetry need
Pro. See [Integrations](guides/integrations.md).

## Next

- Invite your team: **Settings → Members** ([roles](guides/access.md))
- Plant honeytokens: [guides/honeytokens.md](guides/honeytokens.md) (Pro)
- Generate audit evidence: [guides/compliance.md](guides/compliance.md)
- Automate with the API: [api/README.md](api/README.md)
