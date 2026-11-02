# Hardware Inventory

Everything with a power cord in the Stetter Homelab, as probed on 2026-10-30.

## Overview

| Host | Role | IP | Status |
|------|------|----|--------|
| nexus | Primary Proxmox hypervisor (ctr01, dev01, sec01, ci01) | 192.168.1.12 | Active |
| studio | Mac Studio: local AI inference, Open WebUI, Hermes agent | 192.168.1.95 | Active |
| pve-tc1 | Proxmox host for Home Assistant | 192.168.1.11 | Active |
| syn | Synology NAS: storage, primary DNS, GitLab VM | 192.168.1.4 | Active |
| rtr | UniFi Dream Machine Pro: gateway and firewall | 192.168.1.1 | Active |
| core.rsdn.io | Former Kubernetes sandbox | 192.168.1.5 | Offline |

## Compute

### nexus (Minisforum MS-A2)

The main hypervisor. Every Docker stack runs here, inside ctr01.

| Component | Specification |
|-----------|---------------|
| **CPU** | AMD Ryzen 9 9955HX (16C/32T) |
| **RAM** | 64 GB DDR5 |
| **GPU** | NVIDIA RTX 2000E Ada, 16 GB (passed through to ctr01) |
| **Storage** | 1 TB Kingston NVMe (Proxmox, `local`/`local-lvm`) + 4 TB Samsung 990 EVO Plus (ZFS pool `vm-storage`, VM disks) |
| **Network** | `vmbr0` 192.168.1.12 (LAN), `vmbr1` 10.0.10.1 (10GbE DAC to the Synology) |
| **OS** | Proxmox VE 9.2 |

| Guest | Type | vCPU | RAM | Disk | OS | Purpose |
|-------|------|------|-----|------|----|---------|
| 100 ctr01 | VM | 10 | 32 GB | 600 GB | Debian 13 | Docker host, GPU passthrough |
| 101 dev01 | VM | 2 | 4 GB | 100 GB | Ubuntu 26.04 | Bastion / dev box |
| 110 sec01 | VM | 4 | 12 GB | 120 GB | Kali Rolling | Security testing |
| 502 ci01 | LXC | 4 | 4 GB | 32 GB | Debian 13 | Planned OpenTofu CI runner (provisioned, runner not installed yet) |
| 501 mail-bridge | LXC | - | - | - | - | Stopped |

Templates 9000-9003 and 9100 are kept for cloning (see [VM Platform](../infrastructure/vm-platform.md)).

The RTX 2000E is shared by Ollama (Home Assistant's voice LLM), Plex/Jellyfin/Emby/Tdarr/Tunarr/Dispatcharr transcoding, and the ARM ripper. Frigate is currently disabled to give Ollama the VRAM.

### studio (Mac Studio)

Added in 2026 as the local AI box. See [Mac Studio](../infrastructure/mac-studio.md) and [Local AI](ai.md).

| Component | Specification |
|-----------|---------------|
| **Chip** | Apple M5 Max (18 cores: 6 Super + 12 Performance) |
| **Memory** | 64 GB unified; GPU wired limit raised to 56 GiB |
| **Storage** | 1 TB internal (models, OrbStack, Nix) + 2 TB external SSD `studio-ssd` (Parallels VMs and games only) |
| **Network** | Ethernet 192.168.1.95 (Wi-Fi stays on for Apple Watch unlock) |
| **OS** | macOS 27 |

### pve-tc1 (Lenovo ThinkCentre M720q)

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core i5-8400T (6C) |
| **RAM** | 16 GB |
| **Network** | 1GbE, 192.168.1.11 |
| **OS** | Proxmox VE 9.2 |

| Guest | Type | RAM | Disk | Purpose |
|-------|------|-----|------|---------|
| 100 homeassistant | VM (HAOS) | 8 GB | 128 GB | Home Assistant, 192.168.1.3 |

!!! note "Dedicated host"
    Home Assistant stays on its own box so home automation survives nexus maintenance. Its voice LLM runs on ctr01, so voice commands do need nexus.

### core.rsdn.io (offline)

Dual-Xeon Supermicro build with 256 GB DDR3 that hosted the K3s, Talos and NixOS clusters. It doesn't answer on the network as of 2026-10-30; its docs are under [Archive](../infrastructure/k8s-platform.md). The old GPU host `gpu.rsdn.io` (192.168.1.10) is retired too.

## Storage

### syn (Synology DS1621+)

| Component | Specification |
|-----------|---------------|
| **CPU** | AMD Ryzen V1500B |
| **RAM** | 32 GB DDR4 ECC |
| **Network** | E10G21-F2 dual 10GbE (10.0.10.4, DAC to nexus) + 1GbE (192.168.1.4) |
| **OS** | DSM 7.4 |
| **Capacity** | ~42 TB SHR, ~59% used |

**NFS exports used by ctr01** (over the 10GbE link): `/volume1/docker`, `/volume1/media`, `/volume1/gitlab-mirror`, `/volume1/frigate`. The Studio mounts `/volume1/media` read-only at `/nas`. nexus mounts the NAS as Proxmox storage `synology` for backups; pve-tc1 uses CIFS.

**Runs on the NAS:** Technitium DNS (primary), Pi-hole, node-exporter (Container Manager), and the GitLab CE VM (Virtual Machine Manager, 192.168.1.156). See [Synology Stacks](../stacks/synology.md).

## Network

| Device | Model | IP |
|--------|-------|----|
| rtr | UniFi Dream Machine Pro | 192.168.1.1 |
| switch | UniFi US-16-150W | 192.168.1.2 |
| ap-u6 | UniFi U6+ | 192.168.1.7 |

See [Network Topology](network.md).

## Client Devices

| Device | Notes |
|--------|-------|
| MacBook Air M4 15" (24 GB) | Daily laptop, `air` 192.168.1.176, tailnet `air-ts`. Shares the mac-config setup with the Studio |
| iPad | Client only |
| iPhone | Client only, on the tailnet |
| ThinkCentre desktop `bluefin` | Bluefin Linux, 192.168.1.13, tailnet `bluefin-tc1-ts` |

The MacBook Pros are gone; the Studio and the Air replaced them.

## Monitoring

All hosts are scraped by Prometheus on ctr01: node-exporter on nexus, pve-tc1, ctr01, the Synology, Home Assistant and the Studio; pve-exporter for both Proxmox nodes; SNMP for the Synology; unpoller for UniFi; DCGM for the RTX 2000E; macmon for the Studio's GPU, power and temperatures. See [Prometheus](../services/prometheus.md).
