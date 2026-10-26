# Installing on Linux hosts

The Linux sensor is an XDP/eBPF engine plus a small bridge that talks to the
control plane. It installs from a signed package repository, needs no reboot,
and starts **observe-only**.

## Requirements

| | |
|---|---|
| Distribution | Debian, Ubuntu, RHEL, AlmaLinux, Rocky Linux, Fedora or Amazon Linux 2023 |
| Architecture | x86_64 or ARM64 |
| Kernel | 5.4 or later (live XDP attach). The process profiler also needs BTF at `/sys/kernel/btf/vmlinux` |
| Access | root (`sudo`) |
| Network | Outbound HTTPS to `api.prosentriq.com` (or your own control plane) and `packages.prosentriq.com` |

IPv4 and IPv6 traffic are both inspected.

## 1. Get an enrollment key

In the console, open **Sensors → Create enrollment key**. Keys can be limited
in how many hosts may use them, and they expire after 30 days by default (up
to 365). The console shows the commands below with your key filled in.

## 2. Run the installer

```bash
curl -fsSL https://prosentriq.com/install.sh | sudo bash
```

With no key option the installer asks for the key on the terminal with input
hidden. This works under `curl … | sudo bash` too. Any local user can read
command lines with `ps`, so prefer the prompt or a file over `--enroll-key`:

```bash
curl -fsSL https://prosentriq.com/install.sh | sudo bash -s -- --enroll-key-file /root/psq.key
```

The installer also reads `PROSENTRIQ_ENROLL_KEY` from the environment. It
never puts the key on a command line itself.

Want to check the installer before running it? Download it with its Sigstore
bundle from [PROSENTRIQ/releases](https://github.com/PROSENTRIQ/releases) and
[verify it](../security/verifying-releases.md) first.

### What the installer does, in order

1. It checks the key with the control plane. Nothing on the host has changed yet.
2. It detects the interface, kernel and distribution (`--iface` overrides the interface).
3. It writes `/etc/prosentriq/prosentriq.state` (`MODE=trial`, the interface, the control plane).
4. It installs the package from the signed repository only. The repository key's
   fingerprint is pinned inside the released `install.sh` (apt `signed-by=`, or
   dnf `gpgcheck=1` and `repo_gpgcheck=1`).
5. It enrolls the host. The sensor's credential is stored in
   `/etc/prosentriq/bridge.json` (mode 0600). Then it starts `prosentriq-loader`,
   `prosentriq-ai` and `prosentriq-bridge`.

### Options

| Flag | Purpose |
|---|---|
| `--enroll-key KEY` | The enrollment key (`psqe_…`). Visible in `ps` while the installer runs; prefer the prompt or a file |
| `--enroll-key-file FILE` | Read the enrollment key from a file |
| `--iface NAME` | Interface for the XDP probe. Default: the default-route interface |
| `--mode trial\|production` | Start mode. Default `trial` (observe-only probe). `production` needs a paid plan |
| `--package FILE` | Install a local `.deb` or `.rpm` instead of using the repository (air-gapped hosts) |
| `--api-base URL` | Your self-hosted control plane. Default `https://api.prosentriq.com` |
| `--repo-url URL` | A mirror of the package repository. Default `https://packages.prosentriq.com` |
| `--channel stable\|testing` | Release channel. Default `stable`. `testing` gets each release first: use it for staging and early-update hosts |
| `--dry-run` | Validate everything and print the plan; change nothing |
| `--key`, `--key-file` | Legacy v1 agent accounts only |

## 3. Check the host

```bash
sudo prosentriq-ctl status
```

This shows the mode, interface and autonomy level. The host appears as fresh on
**Sensors** within a minute.

## Observe and enforce

A new host runs `prosentriq_observe.o`, whose only exit returns `XDP_PASS`. It
cannot drop or redirect a packet, whatever the control plane says. To enforce,
switch the host's **Mode** to *enforce* on the Sensors page (paid plans). The
bridge applies the change on its next heartbeat. What is then enforced
automatically depends on the [Autonomy Dial](../concepts/autonomy.md).

## Packages without the installer

The installer only configures the repository and enrolls the host. You can do
the same with your own configuration management:

| | Repository | Key |
|---|---|---|
| apt | `https://packages.prosentriq.com/apt {stable,testing} main` | `/usr/share/keyrings/prosentriq-archive-keyring.gpg` via `signed-by=` |
| dnf | `https://packages.prosentriq.com/rpm/{stable,testing}/$basearch` | `/etc/pki/rpm-gpg/RPM-GPG-KEY-prosentriq` with `gpgcheck=1` and `repo_gpgcheck=1` |

The packages are `prosentriq-enterprise` (.deb) and `prosentriq-agent` (.rpm).
Each release's packages, with Sigstore bundles and SBOMs, are also on
[PROSENTRIQ/releases](https://github.com/PROSENTRIQ/releases). For an
air-gapped host, copy the package over and run the installer with `--package`.

## Upgrades

Upgrade through your package manager (`apt upgrade`, `dnf upgrade`), or let the
updater do it. Updates run only through `prosentriq-ota-updater.service`, which
refuses any source that isn't signed with the pinned Prosentriq key. See
[On the host](../guides/host.md#upgrades).

## Uninstall

```bash
sudo apt remove prosentriq-enterprise     # Debian, Ubuntu
sudo dnf remove prosentriq-agent          # RHEL family, Fedora, Amazon Linux
```

Then retire the host on the **Sensors** page so it stops counting as a sensor.

## Next

- [On the host](../guides/host.md): `prosentriq-ctl`, the kill-switch, the local dashboard, isolation, Threat Hub peering
- [Troubleshooting](../troubleshooting.md#linux-sensor)
