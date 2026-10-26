# On the host

What runs on a Linux host, and how to control it locally.

## Services and files

| | |
|---|---|
| `prosentriq-loader` | Attaches the XDP program to the interface |
| `prosentriq-ai` | The local engine: profiler, file integrity, honeypot, scoring, local Autonomy Gate and circuit breaker |
| `prosentriq-bridge` | Talks to the control plane: heartbeats, directives, events, the signed immunity feed |
| `prosentriq-ota-updater.service` | Applies updates, only from sources signed with the pinned Prosentriq key |
| `/etc/prosentriq/prosentriq.state` | Mode, interface and control plane |
| `/etc/prosentriq/bridge.json` | The sensor's credential and settings (mode 0600) |
| `/var/log/prosentriq/` | Logs |

Check a service with `systemctl status prosentriq-bridge` and its log with
`journalctl -u prosentriq-bridge`.

## `prosentriq-ctl`

| Command | Effect |
|---|---|
| `sudo prosentriq-ctl status` | Mode, interface and autonomy level |
| `sudo prosentriq-ctl kill-switch` | Detach every XDP program from the interface, in every attach mode, and stop the agent |
| `sudo prosentriq-ctl dashboard-token` | Print the token for the local dashboard |

Enforcement on a host enrolled with a control plane is switched from the
console (Sensors → Mode), not locally. `enable-enforcement` and
`disable-enforcement` are for legacy v1 installs only.

## The kill-switch

```bash
sudo prosentriq-ctl kill-switch
```

Traffic is untouched the moment it returns: every XDP program is detached and
the agent is stopped. Use it if you ever suspect Prosentriq of interfering with
traffic. To turn protection back on:

```bash
sudo systemctl start prosentriq-loader prosentriq-ai
```

The engine also fails open on its own: if it crashes or stops, packets pass.

## The local dashboard

Each host has an optional dashboard on the loopback interface only:

```bash
ssh -L 8090:127.0.0.1:8090 you@host
```

Open http://127.0.0.1:8090 and paste the token from
`sudo prosentriq-ctl dashboard-token`. The engine's local API on
`127.0.0.1:18080` needs the same token on every `/api/` route.

## Host isolation

At Autonomy level 5, or by hand (**Approvals & actions**, or `isolate_host`
through the API or SOAR), a compromised host can be isolated. It keeps:

- loopback and already-established connections
- the control plane, so it can be released again
- DNS to the host's own resolvers only (`/etc/resolv.conf`, or
  systemd-resolved's upstream servers), so DNS can't be used as a tunnel out

If the resolvers can't be determined (for example a local caching resolver
with unknown upstreams), DNS stays open and the bridge logs a warning. Name
them in `/etc/prosentriq/bridge.json`:

```json
{ "isolation_dns_servers": ["10.0.0.2", "10.0.0.3"] }
```

Release the host with **Undo**, or `release_host`.

## Threat Hub peering (self-managed mesh)

Hosts can also exchange blocklists directly with each other. Peering runs only
over TLS, with each host pinned to the other's certificate (a per-host
self-signed certificate in `/etc/prosentriq/threathub/`, created on install).
It is off until a host is told where to listen:

```bash
echo 10.0.4.12 | sudo tee /etc/prosentriq/threathub/peer_listen    # this host's LAN address, 0.0.0.0, or [::]
sudo /var/lib/dpkg/info/prosentriq-enterprise.postinst configure    # on RPM systems, reinstall the package instead
```

The setting survives upgrades. To stop listening, delete the file and run the
same command again.

Peers connect on TCP 5443 (`PROSENTRIQ_THREATHUB_PEER_PORT`). Only the four
peer-to-peer endpoints are reachable there; managing peers stays on the
loopback dashboard. When you pair two hosts, compare the fingerprint the
dashboard shows for the other host with the one that host shows for itself
(**Threat Hub → Connect a peer**). Peers paired before TLS show **Pair again**:
revoke them and connect again. Nothing is sent to them until then.

For most fleets the [Collective Immunity Network](../concepts/immunity-network.md)
does this for you, without any host-to-host connections.

## Upgrades

Hosts upgrade through the package repository they were installed from:

```bash
sudo apt update && sudo apt upgrade prosentriq-enterprise    # Debian, Ubuntu
sudo dnf upgrade prosentriq-agent                            # RHEL family, Fedora, Amazon Linux
```

Use the `testing` channel on a few staging hosts to get each release first
(`--channel testing` at install time). Every package is signed, and
`prosentriq-ota-updater.service` refuses any source that isn't signed with the
pinned Prosentriq key. No reboot is needed, and the host keeps its credential
and settings.

## Uninstall

```bash
sudo apt remove prosentriq-enterprise     # Debian, Ubuntu
sudo dnf remove prosentriq-agent          # RHEL family, Fedora, Amazon Linux
```

Then retire the host on the **Sensors** page.
