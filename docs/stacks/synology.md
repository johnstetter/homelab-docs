# Synology Stacks

The Synology (`syn`, 192.168.1.4, DSM 7.4) runs the few things that must keep working while ctr01 or nexus is down: primary DNS and GitLab.

## Containers (Container Manager)

Compose files live in `/volume1/docker/stacks/<name>/` on the NAS.

| Container | Image | Network | Purpose |
|-----------|-------|---------|---------|
| technitium | `technitium/dns-server:15.6.2` | bridge, ports 53, 5380, 53443 | **Primary DNS** for `rsdn.io`, ad blocking. UI: `technitium-syn.rsdn.io` |
| node-exporter | `prom/node-exporter` | host | Metrics on :9100 for Prometheus (`synology-node-exporter`) |
| pihole | `pihole/pihole` | host, web on 8118 | Legacy. `restart: "no"` since Technitium took over, but it was still running on 2026-10-30. UI: `pihole.rsdn.io` |

The `gitlab-runner` directory there holds only a README and no running service.

SNMP metrics come from DSM itself (`synology-snmp` job, via snmp-exporter on ctr01).

## GitLab CE VM

GitLab moved out of a container on ctr01 into a VM in Synology Virtual Machine Manager, so the Git server no longer depends on the Docker host it deploys to.

| Property | Value |
|----------|-------|
| **Address** | 192.168.1.156 |
| **URL** | [gitlab.rsdn.io](https://gitlab.rsdn.io) via Traefik (file provider, `https://192.168.1.156`) |
| **OS** | Debian 13 |
| **Metrics** | Prometheus job `gitlab` |
| **Fed by** | `gitlab-mirror` on ctr01, which mirrors GitLab.com into it |

GitLab.com remains the primary forge; CI runs there. The self-hosted instance is a mirror and a fallback.

## Storage Served to Other Hosts

| Export / share | Consumers |
|----------------|-----------|
| `/volume1/docker` | ctr01 (NFS, 10GbE): app data, Traefik certs, Vault, restic repo |
| `/volume1/media` | ctr01 (rw), Studio (`/nas`, ro) |
| `/volume1/frigate` | ctr01 |
| `/volume1/gitlab-mirror` | ctr01 |
| Proxmox storage `synology` | nexus (NFS), pve-tc1 (CIFS): vzdump backups |

## Operations

```bash
ssh syn
cd /volume1/docker/stacks/technitium
sudo docker compose up -d
sudo docker ps
```

!!! warning "DNS changes"
    Restarting Technitium on the NAS drops DNS for the whole LAN until it's back; ctr01's secondary answers in the meantime. Do it from a machine that also has 192.168.1.20 as a resolver.
