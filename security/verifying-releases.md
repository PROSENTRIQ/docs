# Verifying releases

Everything Prosentriq ships is signed, so you can check it was built by our
release workflow before you install it.

| What | Where | Signed with |
|---|---|---|
| `install.sh` | [PROSENTRIQ/releases](https://github.com/PROSENTRIQ/releases/releases), and `https://prosentriq.com/install.sh` | Sigstore bundle (`install.sh.sigstore.json`) |
| `.deb` and `.rpm` packages, x86_64 and ARM64 | The release, and the apt and dnf repositories | Sigstore bundles; the repositories with our GPG archive key |
| SBOMs (SPDX) | The release | Sigstore bundles |
| `SHA256SUMS` | The release | Covers every file in the release |
| The sensor image `ghcr.io/prosentriq/agent` | GitHub Container Registry | Sigstore (cosign), with provenance |
| The Helm chart `oci://ghcr.io/prosentriq/charts/prosentriq-agent` | GitHub Container Registry | Sigstore (cosign) |

Signing is keyless: the signature proves the artifact was built by the
workflow `PROSENTRIQ/prosentriq-core/.github/workflows/release.yml` from a
release tag. Signatures are recorded in the public Rekor transparency log.
Install [cosign](https://docs.sigstore.dev/cosign/system_config/installation/)
to check them. If a check fails, don't install.

## The installer and packages

Download the file and its `.sigstore.json` bundle from the release, then:

```bash
cosign verify-blob install.sh --bundle install.sh.sigstore.json \
  --certificate-identity-regexp '^https://github.com/PROSENTRIQ/prosentriq-core/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

The same command works for each `.deb`, `.rpm` and SBOM with its own bundle.
To check the checksums: `sha256sum -c SHA256SUMS --ignore-missing`.

## Images and the Helm chart

Verify by digest, not by tag:

```bash
cosign verify ghcr.io/prosentriq/agent@sha256:… \
  --certificate-identity-regexp '^https://github.com/PROSENTRIQ/prosentriq-core/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com

cosign verify ghcr.io/prosentriq/charts/prosentriq-agent@sha256:… \
  --certificate-identity-regexp '^https://github.com/PROSENTRIQ/prosentriq-core/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Each release's notes list the digests. The Helm chart in the
[helm-charts](https://github.com/PROSENTRIQ/helm-charts) repository pins the
sensor image by digest.

## The package repositories

`install.sh` configures apt or dnf with our repository key and pins its
fingerprint, so your package manager checks every package it installs:

- apt: `signed-by=/usr/share/keyrings/prosentriq-archive-keyring.gpg`
- dnf: `gpgcheck=1` and `repo_gpgcheck=1` with `/etc/pki/rpm-gpg/RPM-GPG-KEY-prosentriq`

The archive key is kept offline and is separate from the keys above.

## The Python SDK

The SDK is published to PyPI from [prosentriq-sdk-python](https://github.com/PROSENTRIQ/prosentriq-sdk-python)
with PyPI Trusted Publishing, from release tags only.

More on verification: [PROSENTRIQ/releases/VERIFY.md](https://github.com/PROSENTRIQ/releases/blob/main/VERIFY.md).
