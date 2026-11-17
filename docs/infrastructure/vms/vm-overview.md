# Virtual Machine Overview

Every Proxmox guest, as listed by `qm list` / `pct list` on 2026-10-30.

## Hypervisors

| Host | Hardware | Proxmox | Guests |
|------|----------|---------|--------|
| nexus (192.168.1.12) | MS-A2, Ryzen 9 9955HX, 64 GB | 9.2 | ctr01, dev01, sec01, ci01, mail-bridge, templates |
| pve-tc1 (192.168.1.11) | ThinkCentre, i5-8400T, 16 GB | 9.2 | homeassistant |

core.rsdn.io, which hosted the Kubernetes and Talos clusters, is offline. See [Archive](../k8s-platform.md).

## nexus

| ID | Name | Type | vCPU | RAM | Disk | Networks | State |
|----|------|------|------|-----|------|----------|-------|
| 100 | [ctr01](ctr01/README.md) | VM | 10 | 32 GB | 600 GB | LAN .20, storage 10.0.10.20 | Running |
| 101 | [dev01](dev01/README.md) | VM | 2 | 4 GB | 100 GB | LAN .21 | Running |
| 110 | [sec01](sec01/README.md) | VM | 4 | 12 GB | 120 GB | LAN .25, storage 10.0.10.25 | Running |
| 502 | ci01 | LXC | 4 | 4 GB | 32 GB | LAN .22 | Running, no runner yet |
| 501 | mail-bridge | LXC | - | - | - | - | Stopped |

VM disks are on the ZFS pool `vm-storage` (4 TB Samsung 990 EVO Plus); ci01's root is on `local-lvm`. Memory is tight: nexus has ~60 GB usable and the running guests are allocated 52 GB.

## pve-tc1

| ID | Name | Type | RAM | Disk | Address |
|----|------|------|-----|------|---------|
| 100 | homeassistant | VM (HAOS) | 8 GB | 128 GB | 192.168.1.3 |

pve-tc1's local storage is ~80% full.

## Roles

**ctr01**: the Docker host. Every stack, Traefik, monitoring, the GPU workloads. RTX 2000E passed through via Proxmox resource mappings. See [ctr01 Stacks](../../stacks/ctr01.md).

**dev01**: SSH bastion and dev box. Its host key is in every managed host's `authorized_keys`, so it can reach the whole lab.

**sec01**: Kali for security testing, with a storage-network NIC for large datasets. See the sec01 pages for X11 forwarding and tools.

**ci01**: LXC created for the vm-platform OpenTofu runner (issue #118). Debian 13, nothing installed yet.

## Access

```bash
ssh ctr01            # stetter, passwordless sudo
ssh dev01
ssh sec01
ssh -X sec01         # GUI tools
ssh nexus 'sudo qm list; sudo pct list'
ssh pve-tc1 'sudo qm list'
```

The Hermes agent logs in to ctr01, dev01, sec01, nexus and pve-tc1 as the restricted `hermes` user. See [Hermes](../../services/hermes.md).

## Backups

- **Guests:** weekly vzdump of nexus guests to the Synology (`proxmox_backup` role in vm-platform). LXC backups stage their temp files on local disk.
- **Container data:** Backrest/restic from inside ctr01. See [Backup & Restore](../../runbooks/backup-restore.md).

## Related

- [VM Platform](../vm-platform.md)
- [VM Lifecycle](../../runbooks/vm-lifecycle.md)
- [Hardware](../../architecture/hardware.md)
