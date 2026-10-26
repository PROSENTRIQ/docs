# Signing keys

A control plane signs three things with one Ed25519 key: evidence packs
(auditors verify them), the Immunity Network feed (every sensor verifies it
against the key it pinned at enrollment), and federation contributions. Choose
the key with `PROSENTRIQ_SIGNER`.

The hosted service's key is published in [Signatures](../api/signatures.md#the-hosted-services-key).
This page is for Enterprise customers running their own control plane.

| `PROSENTRIQ_SIGNER` | Key setting | Where the private key lives | Signed directly up to |
|---|---|---|---|
| `local` | `PROSENTRIQ_SIGNING_KEY` or `PROSENTRIQ_SIGNING_KEY_FILE` (from `prosentriq gen-signing-key`) | The control plane's memory | No limit |
| `gcp-kms` | `PROSENTRIQ_GCP_KMS_KEY_NAME`, algorithm `EC_SIGN_ED25519` | Google Cloud KMS (software protection level: Cloud KMS has no HSM Ed25519) | 64 KiB |
| `aws-kms` | `PROSENTRIQ_AWS_KMS_KEY_ID` (and `PROSENTRIQ_AWS_REGION`), key spec `ECC_NIST_EDWARDS25519` | AWS KMS HSMs | 4 KiB |
| `vault` | `PROSENTRIQ_VAULT_ADDR`, `PROSENTRIQ_VAULT_TRANSIT_KEY`, `PROSENTRIQ_VAULT_TOKEN` or `_TOKEN_FILE`; Transit key type `ed25519` | HashiCorp Vault or OpenBao (Transit) | 64 KiB |

All of them produce plain Ed25519 signatures that any library can verify.
Documents larger than the limit are signed through a fixed SHA-512 digest
envelope (`"digest": "sha512"` in the signature record; see
[Signatures](../api/signatures.md#ed25519-the-control-planes-signing-key)).
Sensors running an older SDK may not verify envelope-signed feeds, so upgrade
them to the current release before switching to `aws-kms`, where every feed is
larger than 4 KiB.

Every signature a remote provider returns is checked against the public key
read at start-up before it is used. A re-pointed alias, a rotated key version
or a misbehaving provider therefore fails loudly instead of publishing
signatures that sensors would reject.

## Check the key

```bash
prosentriq signing-key
# signer:     aws-kms
# key id:     ed25519:3f0c…
# public key: …
# sign     64-byte document (direct): ok
# sign 131136-byte document (digest envelope): ok
```

Publish the key id and public key (for example on your intranet or in your
`security.txt`) so auditors can check packs offline.

## Google Cloud KMS

```bash
gcloud kms keyrings create prosentriq --location=europe-west2
gcloud kms keys create signing --keyring=prosentriq --location=europe-west2 \
  --purpose=asymmetric-signing --default-algorithm=ec-sign-ed25519 --protection-level=software
# Least privilege for the control plane's service account (workload identity on GKE):
for role in roles/cloudkms.signer roles/cloudkms.publicKeyViewer; do
  gcloud kms keys add-iam-policy-binding signing --keyring=prosentriq --location=europe-west2 \
    --member=serviceAccount:prosentriq-platform@PROJECT.iam.gserviceaccount.com --role=$role
done
# PROSENTRIQ_SIGNER=gcp-kms
# PROSENTRIQ_GCP_KMS_KEY_NAME=projects/PROJECT/locations/europe-west2/keyRings/prosentriq/cryptoKeys/signing/cryptoKeyVersions/1
```

Name the key **version** (`…/cryptoKeyVersions/1`). Creating version 2 changes
nothing until you point the setting at it and endorse it (below).

## AWS KMS

```bash
KEY=$(aws kms create-key --key-spec ECC_NIST_EDWARDS25519 --key-usage SIGN_VERIFY \
        --description "Prosentriq evidence and immunity feed signing" --query KeyMetadata.Arn --output text)
aws kms create-alias --alias-name alias/prosentriq-signing --target-key-id "$KEY"
# PROSENTRIQ_SIGNER=aws-kms
# PROSENTRIQ_AWS_KMS_KEY_ID=alias/prosentriq-signing
# PROSENTRIQ_AWS_REGION=eu-west-2
```

IAM policy for the control plane's role (IRSA or EKS Pod Identity; avoid static
access keys):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["kms:Sign", "kms:GetPublicKey"],
    "Resource": "arn:aws:kms:eu-west-2:ACCOUNT:key/KEY-ID",
    "Condition": {"StringEquals": {"kms:SigningAlgorithm": "ED25519_SHA_512"}}
  }]
}
```

The alias is resolved once at start-up, and the control plane then signs with
that key's ARN, so re-pointing the alias never switches keys under a running
process.

## HashiCorp Vault or OpenBao (Transit)

```bash
vault secrets enable transit
vault write -f transit/keys/prosentriq-signing type=ed25519     # not derived, not exportable
vault policy write prosentriq-signing - <<'HCL'
path "transit/sign/prosentriq-signing" { capabilities = ["update"] }
path "transit/keys/prosentriq-signing" { capabilities = ["read"] }
HCL
# PROSENTRIQ_SIGNER=vault
# PROSENTRIQ_VAULT_ADDR=https://vault.internal:8200
# PROSENTRIQ_VAULT_TRANSIT_KEY=prosentriq-signing
# PROSENTRIQ_VAULT_TOKEN_FILE=/run/secrets/vault-token     # e.g. written by Vault Agent; re-read on every call
# Optional: PROSENTRIQ_VAULT_TRANSIT_MOUNT, _NAMESPACE, _CA_FILE, _TRANSIT_KEY_VERSION
```

The key version is pinned at start-up (the latest, or
`PROSENTRIQ_VAULT_TRANSIT_KEY_VERSION`), so rotating the Transit key has no
effect until you restart and endorse.

## Changing the key

Every sensor pinned the current key at enrollment, every federated peer pinned
it for your feed, and every evidence pack names the key that signed it. When
you switch provider (for example `local` to `aws-kms`) or rotate, the previous
key endorses the new one and all of them keep working:

```bash
# 1. Configure the new signer and restart. Sensors ignore feeds signed by a key
#    they haven't seen endorsed, so nothing changes for them yet.
# 2. Have the previous key sign an endorsement of the new one:
prosentriq endorse-signing-key --previous-signer local --previous-key /secure/old-seed
#    (--previous-signer gcp-kms|aws-kms|vault --previous-key <key version / key id / transit key>
#     [--previous-key-version N for Vault])
```

Then:

- **Sensors** see `signing_key_id` change in their heartbeat, fetch
  `GET /v2/public/signing-key`, walk the endorsement chain from the key they
  pinned, and re-pin. The bridge saves the new key in
  `/var/lib/prosentriq/signing_key.json`.
- **Auditors** keep verifying old packs: each pack names its own key, and
  `POST /v2/public/evidence/verify` checks the key a pack names, or the current
  key and the five most recent previous ones.
- **Federated peers** follow the same chain on their next sync.

Keep the previous key until the endorsement is published, then retire it.

**If a key leaked, do not endorse.** A leaked key could endorse an attacker's
key just as easily. Instead, configure a new key, re-enroll the sensors (or
replace `signing_public_key` in their configuration and delete
`/var/lib/prosentriq/signing_key.json`), and give federated hubs and peers the
new key out of band.

## Package signing is separate

Packages and repositories are signed with Prosentriq's offline GPG archive
key, and releases and images with keyless Sigstore signatures. Neither uses
this key. See [Verifying releases](../security/verifying-releases.md).
