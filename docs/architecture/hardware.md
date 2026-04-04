# Hardware Inventory

Complete inventory of all hardware in the Stetter Homelab.

## Overview

| Host | Role | Location | Status |
|------|------|----------|--------|
| pve-ms-a2 | Primary Hypervisor | Rack | Active |
| core.rsdn.io | K8s Development Sandbox | Rack | Active |
| pve-tc1 | Home Automation | Rack | Active |
| syn | NAS/Storage | Rack | Active |
| rtr | Network Gateway | Rack | Active |

## Compute

### pve-ms-a2 (Primary Hypervisor)

**Minisforum MS-A2**

| Component | Specification |
|-----------|---------------|
| **CPU** | AMD Ryzen 9 9955HX |
| **RAM** | 64GB DDR5 |
| **GPU** | NVIDIA RTX 2000E ADA |
| **Storage** | NVMe SSD (OS + VMs) |
| **Network** | 2.5GbE + 10GbE (via Synology) |
| **IP Address** | 192.168.1.12 |
| **OS** | Proxmox VE 8.x |

**Hosted VMs:**

| VM | vCPUs | RAM | Disk | OS | Purpose |
|----|-------|-----|------|-----|---------|
| ctr01 | 8 | 32GB | 100GB | Debian 13 | Docker Host |
| dev01 | 4 | 16GB | 50GB | Ubuntu 24.04 | Dev/Bastion |

**GPU Passthrough:**

The RTX 2000E ADA is passed through to ctr01 for:

- Plex hardware transcoding
- Frigate object detection
- Ollama LLM inference
- Whisper speech-to-text

### core.rsdn.io (K8s Development Sandbox)

**Supermicro X9DRL-3F/iF Custom Build**

| Component | Specification |
|-----------|---------------|
| **CPU** | Dual Intel Xeon E5-2670 v1 @ 2.60GHz (32C total: 2×8C×2T) |
| **RAM** | 256GB DDR3 ECC |
| **Storage** | Multiple NVMe + SATA (VMs + Templates) + 42TB NFS storage |
| **Network** | 1GbE + NFS access to Synology |
| **IP Address** | 192.168.1.5 |
| **OS** | Proxmox VE 8.x |

**Role:** Kubernetes and Talos Linux development sandbox with extensive VM experimentation capacity.

**Active VM Projects:**

| Project | VM Range | Count | Specs | Purpose |
|---------|----------|-------|-------|---------|
| **Production K3s** | 106-115 | 7 VMs | 16GB each | HA K8s cluster |
| **Talos Development** | 126-131 | 6 VMs | 4GB each | Talos Linux testing |
| **NixOS/Terraform** | 120-125 | 6 VMs | 2-4GB each | Infrastructure-as-code |
| **RHEL Testing** | 100-102 | 3 VMs | 8GB each | Enterprise Linux testing |
| **Utility** | 200 | 1 VM | 8GB | Ansible automation |
| **Templates** | 9000+ | 3 templates | - | Debian, Ubuntu, NixOS |

**Total Active VMs:** ~26 VMs utilizing 256GB RAM capacity

**Storage Strategy:**
- **VM Storage**: Local NVMe/SATA for VM disks  
- **Persistent Data**: 42TB NFS mount for container storage
- **Templates**: Optimized Packer-built base images

**Network Configuration:**
- **Management**: 192.168.1.0/24 via main switch
- **Storage**: Direct NFS access to /volume1/* exports
- **Inter-VM**: Isolated networks per project

**Key Projects:**
- **talos-platform**: CLI-based Talos cluster management
- **talos-terraform-poc**: Terraform provider approach
- **k8s-platform**: NixOS-based Kubernetes development

### pve-tc1 (Home Automation)

**Lenovo ThinkCentre**

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core i5 |
| **RAM** | 16GB DDR4 |
| **Storage** | 256GB SSD |
| **Network** | 1GbE |
| **IP Address** | 192.168.1.11 |
| **OS** | Proxmox VE 8.x |

**Hosted VMs:**

| VM | vCPUs | RAM | Disk | OS | Purpose |
|----|-------|-----|------|-----|---------|
| Home Assistant | 2 | 4GB | 32GB | HAOS | Home Automation |

!!! note "Dedicated Host"
    Home Assistant runs on a dedicated host for reliability. If the main hypervisor goes down, home automation continues to function.

## Storage

### syn (Synology DS1621+)

**Synology DiskStation DS1621+**

| Component | Specification |
|-----------|---------------|
| **CPU** | AMD Ryzen V1500B |
| **RAM** | 32GB DDR4 ECC |
| **Drive Bays** | 6x 3.5" + 2x NVMe |
| **Network** | 10GbE + 4x 1GbE |
| **IP Address** | 192.168.1.4 |
| **OS** | DSM 7.x |

**Storage Pools:**

| Pool | Type | Capacity | RAID | Purpose |
|------|------|----------|------|---------|
| Volume 1 | HDD (5x 10.9TB) | 41.9TB | SHR | Docker, media, backups |

**Cache:**

| Drive | Type | Capacity | Purpose |
|-------|------|----------|---------|
| M.2 Drive 1 | Samsung SSD | 931.5GB | SSD read/write cache |

**NFS Exports:**

| Export | Path | Access | Purpose |
|--------|------|--------|---------|
| docker | /volume1/docker | ctr01 | Container persistent storage |
| media | /volume1/media | ctr01 | Media library |
| backups | /volume1/backups | All hosts | Backup destination |

**Services Running:**

- Docker (Container Manager)
- Technitium DNS (Primary + ad blocking)
- Node Exporter (Metrics)

## Network

### rtr (UniFi Dream Machine Pro)

| Component | Specification |
|-----------|---------------|
| **Model** | UDM-Pro |
| **WAN** | 1Gbps Fiber |
| **LAN Ports** | 8x 1GbE RJ45 |
| **SFP+ Ports** | 2x 10GbE |
| **IP Address** | 192.168.1.1 |

**Features:**

- UniFi Network Controller
- IDS/IPS enabled
- DPI (Deep Packet Inspection)
- Automatic threat management
- VPN server (WireGuard ready)

### Network Switches

| Device | Model | Ports | Location |
|--------|-------|-------|----------|
| Core Switch | UniFi USW-Pro-24-PoE | 24x 1GbE + 2x 10GbE | Rack |

## Power

### UPS

| Device | Model | Capacity | Protected Devices |
|--------|-------|----------|-------------------|
| Primary UPS | APC SMT1500RM2U | 1500VA | All rack equipment |

**Runtime:** ~15 minutes at full load

**Monitoring:** NUT (Network UPS Tools) on syn

## Accessories

### Cameras (Frigate)

| Camera | Model | Location | Resolution |
|--------|-------|----------|------------|
| Front Door | Reolink RLC-810A | Exterior | 4K |
| Garage | Reolink RLC-510A | Interior | 5MP |
| Backyard | Reolink RLC-810A | Exterior | 4K |
| Driveway | Reolink RLC-810A | Exterior | 4K |

All cameras connect to Frigate NVR on ctr01 for:

- 24/7 recording
- Object detection (person, vehicle, animal)
- Home Assistant integration

## Future Hardware Plans

!!! info "Planned Upgrades"

    - [ ] Add second NVMe to Synology for cache
    - [ ] Upgrade pve-tc1 to newer mini PC
    - [ ] Add dedicated backup NAS
    - [ ] 10GbE switch for high-speed backbone

## Hardware Lifecycle

| Host | Purchase Date | Warranty Expires | Replacement Plan |
|------|---------------|------------------|------------------|
| pve-ms-a2 | 2024-Q4 | 2027-Q4 | Evaluate in 2027 |
| pve-tc1 | 2022-Q2 | Expired | Replace 2025 |
| syn | 2023-Q1 | 2026-Q1 | Evaluate in 2026 |
| rtr | 2022-Q1 | Expired | Replace when needed |

## Maintenance

### Regular Maintenance Tasks

| Task | Frequency | Notes |
|------|-----------|-------|
| Firmware updates | Monthly | Check UniFi, Proxmox, DSM |
| Disk health check | Weekly | Automated via SMART |
| Dust cleaning | Quarterly | Physical cleaning |
| UPS battery test | Annually | Run self-test |

### Monitoring

All hardware is monitored via:

- **Prometheus** - Metrics collection
- **Node Exporter** - Host-level metrics
- **SMART** - Disk health
- **SNMP** - Network devices (via UniFi)
