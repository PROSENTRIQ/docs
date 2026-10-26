# Compliance evidence and the auditor portal

Prosentriq records the evidence auditors ask for as it works: what was
monitored, what was detected, what was done about it and how fast. You
generate a signed pack when you need one. Every number in it is computed from
the platform's own records for the period, never typed in.

## Frameworks

| Framework (`id`) | Controls mapped | Plan |
|---|---|---|
| SOC 2, 2017 Trust Services Criteria (`soc2`) | CC6.1, CC7.1, CC7.2, CC7.3, CC7.4 | Starter and up |
| PCI DSS v4.0 (`pci_dss_4`) | 10.2.1, 10.4.1, 10.5.1, 11.5.1, 8.4.2 | Pro and up |
| HIPAA Security Rule (`hipaa`) | 164.312(b), 164.308(a)(1)(ii)(D), 164.308(a)(6)(ii) | Pro and up |
| ISO/IEC 27001:2022 Annex A (`iso27001_2022`) | A.8.15, A.8.16, A.5.25, A.5.26, A.8.5 | Pro and up |
| NIST Cybersecurity Framework 2.0 (`nist_csf_2`) | DE.CM-01, DE.CM-09, DE.AE-02, RS.MI-01, PR.AA-03 | Pro and up |
| NIST SP 800-53 Rev. 5 (`nist_800_53_r5`) | SI-4, AU-6, AU-9, IR-4, IA-2(1) | Pro and up |
| CIS Critical Security Controls v8 (`cis_v8`) | 8.2, 8.11, 13.1, 13.3, 6.5 | Pro and up |
| NIS2 Directive (EU) 2022/2555 (`nis2`) | Art. 21(2)(b), Art. 21(2)(j), Art. 23 | Pro and up |
| DORA Regulation (EU) 2022/2554 (`dora`) | Art. 9, Art. 10, Art. 17 | Pro and up |

Prosentriq provides evidence for these controls. It does not make you
compliant on its own, and your auditor decides what is sufficient.

## Control status

**Compliance → Control status** (`GET /v2/compliance/status`) shows each mapped
control as one of:

| Status | Meaning |
|---|---|
| Evidence present | The records show the control operating in the period |
| No activity | The control is in place, but nothing happened to evidence it (for example, no file-integrity events) |
| Gap | Something an auditor will flag, with the reason. For example, PCI DSS 10.5.1 asks for 12 months of log retention and your plan keeps 90 days |

## Evidence packs

**Compliance → Signed evidence packs → Generate evidence pack**
(`POST /v2/compliance/evidence-packs` with `frameworks` and `days`, 1 to 400,
default 90). For each framework and control, a pack holds the control's status
and the evidence behind it, in these sections: monitoring coverage (hosts
monitored, reporting and enforcing), file integrity, detections and incidents,
explainability, triage, response, the audit log (including the head of your
organization's hash chain, which proves the history hasn't been edited),
retention, access control (MFA and SSO) and integrations.

Packs are canonical JSON signed with the control plane's Ed25519 key. If the
control plane is configured with an RFC 3161 timestamp authority, packs are
also timestamped. Download one with `GET /v2/compliance/evidence-packs/{id}`.
Every download is recorded in the audit log.

**Your auditor can verify a pack offline**, without trusting Prosentriq's
servers: [Verifying an evidence pack](../api/signatures.md#verifying-an-evidence-pack).

## Cyber-insurance pack

**Compliance → Signed evidence packs → Generate cyber-insurance pack** (`POST /v2/compliance/insurance-pack`,
Starter and up) pre-fills common underwriting questions from live data:
monitoring coverage, logging and retention, MFA and SSO enforcement, the
autonomy level in use, and the median time from detection to containment.
It is signed like an evidence pack.

## Auditor portal (Pro)

Give your auditor a read-only, time-boxed link instead of screenshots:
**Compliance → Auditor portal** (`POST /v2/compliance/auditor-links` with a
`label`, the `frameworks` to share, and `expires_days`, 1 to 90, default 14).

The auditor opens the link without an account and sees the control status and
the packs for those frameworks only. Every visit is recorded in your audit log.
Revoke a link at any time (`DELETE /v2/compliance/auditor-links/{id}`).

## The audit log

**Audit log** (`GET /v2/audit-log`) records every privileged action: sign-ins,
MFA changes, keys issued and revoked, autonomy changes, approvals, undos, rule
rollouts, destination changes, evidence exports and Prosentriq support access.
Each entry is hash-chained to the previous one per organization.
`GET /v2/audit-log/verify` recomputes the chain and reports whether it is intact.

## Who can do what

Owners, admins and auditors (the `compliance` permission) generate and download
packs and manage auditor links. Every member can see the control status. See
[Teams and access](access.md).
