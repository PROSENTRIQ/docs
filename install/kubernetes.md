# Installing on Kubernetes

The `prosentriq-agent` Helm chart runs the same XDP/eBPF engine and bridge as
the [Linux sensor](linux.md), as a DaemonSet on every node. Findings carry the
pod, namespace and container image. The profiler reports each process's cgroup
id, and the bridge maps it to a pod using a read-only pods list scoped to its
own node.

The chart's source is public: [PROSENTRIQ/helm-charts](https://github.com/PROSENTRIQ/helm-charts).

## What a node needs

- Linux with BTF (`/sys/kernel/btf`) for XDP/eBPF
- The host network, because XDP attaches to the node's interface (set `interface`)
- The host PID namespace, for process attribution
- These capabilities. The pod is not `privileged`: `BPF`, `PERFMON`,
  `NET_ADMIN`, `SYS_ADMIN`, `SYS_RESOURCE`, `SYS_PTRACE`, `KILL`

Credentials persist per node under `/var/lib/prosentriq-agent`, so a restarted
pod keeps its identity.

## Install

Create an enrollment key in the console (**Sensors → Create enrollment key**).
Keep it in a Secret rather than on the command line:

```bash
kubectl create namespace prosentriq
kubectl -n prosentriq create secret generic prosentriq-enroll --from-literal=enrollKey=psqe_...

helm install prosentriq-agent oci://ghcr.io/prosentriq/charts/prosentriq-agent \
    --version <version> -n prosentriq \
    --set existingSecret=prosentriq-enroll \
    --set interface=eth0
```

Use the version of the latest [release](https://github.com/PROSENTRIQ/releases/releases),
for example `--version 2.0.0-rc.2`. The chart and the sensor image
(`ghcr.io/prosentriq/agent`) are signed. [Verify them](../security/verifying-releases.md)
before installing.

To install from the repository instead:

```bash
git clone https://github.com/PROSENTRIQ/helm-charts
helm install prosentriq-agent ./helm-charts/charts/prosentriq-agent -n prosentriq \
    --set existingSecret=prosentriq-enroll --set interface=eth0
```

Every node starts **observe-only**. Switch nodes to enforce on the **Sensors**
page; each node is a host there.

## Values

| Value | Default | |
|---|---|---|
| `existingSecret` | `""` | Secret with the key `enrollKey` (preferred) |
| `enrollKey` | `""` | The enrollment key itself, if you don't use a Secret |
| `apiBase` | `https://api.prosentriq.com` | Your control plane (self-hosted: your API URL) |
| `interface` | `eth0` | Interface the XDP probe attaches to on every node |
| `image.digest` | the release's digest | Pins the image by digest (wins over `image.tag`) |
| `nodeSelector` | `kubernetes.io/os: linux` | |
| `tolerations` | all | Runs on every node, including tainted ones |
| `resources` | requests 100m CPU, 256Mi; limit 768Mi | |
| `priorityClassName` | `system-node-critical` | |

## Upgrade and uninstall

```bash
helm upgrade prosentriq-agent oci://ghcr.io/prosentriq/charts/prosentriq-agent --version <new> -n prosentriq --reuse-values
helm uninstall prosentriq-agent -n prosentriq
```

After uninstalling, retire the nodes on the **Sensors** page.
