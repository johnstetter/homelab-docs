# VM Platform

[stetter-homelab/vm-platform](https://gitlab.com/stetter-homelab/vm-platform) provisions and configures the Proxmox guests and the Proxmox hosts themselves.

| Tool | Version (devbox) | Used for |
|------|------------------|----------|
| OpenTofu | 1.12 | VMs on nexus via the `bpg/proxmox` provider; state in GitLab's HTTP backend, one state per VM |
| Ansible | 2.20 | Everything after first boot, on guests and on both Proxmox hosts |
| Packer | - | Built templates 9001-9003; dormant since 2026-02 and likely to be dropped |

Work happens in `devbox shell`, which pins the tools above.

## Layout

```
vm-platform/
├── terraform/
│   ├── modules/proxmox-vm/   # bpg/proxmox VM module (UEFI + BIOS)
│   └── vms/
│       ├── ctr01/  dev01/  sec01/
│       ├── _templates/       # scaffolds for new VMs (clone from 9001-9003)
│       └── new-vm.sh
├── ansible/
│   ├── inventory/hosts.yml   # container_hosts, dev_hosts, security_hosts, proxmox_hosts, ci_hosts
│   ├── site.yml
│   ├── playbooks/            # one per concern (below)
│   ├── roles/                # alloy, dev-env, docker-volume-backup, node-exporter,
│   │                         # nvidia-drivers, proxmox_backup, proxmox_storage,
│   │                         # pulse-sensor-proxy, security_tools
│   └── files/hermes/         # hermes-readlog, hermes-docker, hermes-pve wrappers
├── packer/                   # debian-docker-host, ubuntu-server, kali-security-host
└── docs/                     # progress log, runbooks, networking, observability
```

## What It Manages

| Guest / host | Managed by | Notes |
|--------------|-----------|-------|
| ctr01 (VM 100) | OpenTofu + Ansible | 10 vCPU, 32 GB (raised from 24 GB), 600 GB on `vm-storage`, GPU via Proxmox resource mapping `nvidia-rtx2000e-gpu`/`-audio` |
| dev01 (VM 101) | OpenTofu + Ansible | Ubuntu 26.04, bastion and dev environment |
| sec01 (VM 110) | OpenTofu + Ansible | Kali, security tools role |
| ci01 (LXC 502) | Ansible (`ci_hosts`) | Created out-of-band for the OpenTofu CI runner (issue #118); runner not installed yet |
| nexus, pve-tc1 | Ansible (`proxmox_hosts`) | node-exporter, storage, vzdump schedule, Pulse sensor proxy, `hermes` user |

## Playbooks

| Playbook | Does |
|----------|------|
| `site.yml` | Container and security hosts end to end |
| `configure-ctr-host.yml`, `configure-dev-host.yml`, `configure-security-host.yml` | Per-role setup |
| `docker.yml`, `nfs.yml`, `nvidia-drivers` role | Docker CE, NFS mounts over the 10GbE network, NVIDIA drivers + container toolkit |
| `node-exporter.yml`, `alloy.yml` | Metrics and log shipping |
| `docker-volume-backup.yml`, `vault-backup-approle.yml` | Backup plumbing |
| `proxmox-backup.yml` | Weekly vzdump of nexus guests to the Synology |
| `proxmox-storage.yml` | Proxmox storage definitions |
| `gitlab-runner.yml` | Host GitLab Runner |
| `ssh-authorized-keys.yml` | Deploys `ssh_authorized_keys` and sweeps `ssh_revoked_keys` |
| `hermes-user.yml` | Non-root `hermes` user + sudo wrappers on all five managed hosts |
| `deploy-docker-cleanup.yml`, `fix-uid.yml`, `create-stetter-user.yml`, `bootstrap-ansible-user.yml` | Maintenance and bootstrap |

## CI

Stages: lint → security → validate → plan → apply. Changes under `terraform/` get a `tofu plan` per VM (ctr01, dev01, sec01) and a **manual** `tofu apply` job, using the GitLab state backend. Ansible changes get `ansible-lint` and security checks; playbooks are run from devbox. ci01 is meant to become the runner for the OpenTofu jobs.

## SSH Keys

`ansible/inventory/group_vars/all.yml` holds `ssh_authorized_keys` (the shared Mac key, dev01's bastion key, bluefin) and `ssh_revoked_keys`. Dropping a key from the first list doesn't remove it from hosts, so retired keys stay in the second list permanently.

## Templates on nexus

| ID | Name | Source |
|----|------|--------|
| 9000 | debian-12-cloud-template | Cloud image |
| 9001 | debian-13-docker-host | Packer, 2025-12 |
| 9002 | ubuntu-24.04-server | Packer, 2025-12 |
| 9003 | kali-2025.4-security-host | Packer, 2026-02 |
| 9100 | nixos-base-template | NixOS |

The Packer configs have been edited since 9001 was built and never rebuilt, so `packer/` isn't an exact description of what's running.

## Common Operations

```bash
cd vm-platform && devbox shell

# change a VM
cd terraform/vms/ctr01 && tofu plan && tofu apply

# configure
cd ansible
ansible-playbook site.yml -l ctr01
ansible-playbook playbooks/hermes-user.yml
ansible-playbook playbooks/ssh-authorized-keys.yml
```

See [VM Lifecycle](../runbooks/vm-lifecycle.md).
