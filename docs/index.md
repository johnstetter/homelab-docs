# Stetter Homelab Documentation

Welcome to the central documentation hub for the Stetter Homelab infrastructure. This site serves as the single source of truth for all homelab systems, services, and operational procedures.

## Quick Links

<div class="grid cards" markdown>

-   :material-server-network:{ .lg .middle } __Architecture__

    ---

    Network topology, hardware inventory, and system design

    [:octicons-arrow-right-24: Architecture Overview](architecture/index.md)

-   :material-cloud-outline:{ .lg .middle } __Infrastructure__

    ---

    Infrastructure as Code with Packer, OpenTofu, and Ansible

    [:octicons-arrow-right-24: Infrastructure Overview](infrastructure/index.md)

-   :material-docker:{ .lg .middle } __Stacks__

    ---

    Docker Compose stacks running on ctr01 and Synology

    [:octicons-arrow-right-24: Stacks Overview](stacks/index.md)

-   :material-format-list-bulleted:{ .lg .middle } __Services__

    ---

    Complete service catalog with access URLs

    [:octicons-arrow-right-24: Service Catalog](services/index.md)

-   :material-book-open-variant:{ .lg .middle } __Runbooks__

    ---

    Operational procedures and troubleshooting guides

    [:octicons-arrow-right-24: Runbooks](runbooks/index.md)

</div>

## Infrastructure Overview

The Stetter Homelab runs a **hybrid architecture** with specialized Proxmox hosts, Docker containers, Kubernetes clusters, and a Synology NAS for centralized storage.

### Core Components

| Component | Host | Description |
|-----------|------|-------------|
| **Docker Hypervisor** | pve-ms-a2 | Minisforum MS-A2 optimized for Docker workloads + GPU |
| **K8s Sandbox** | core.rsdn.io | Dell PowerEdge for Kubernetes development (256GB RAM) |
| **Docker Host** | ctr01 | Debian 13 VM hosting Docker stacks with RTX2000E ADA |
| **Development** | dev01 | Ubuntu 24.04 VM for development and bastion access |
| **Security Testing** | sec01 | Kali Linux VM for security testing and penetration testing |
| **Kubernetes Clusters** | core.rsdn.io | Production K3s, Talos Linux, and NixOS dev clusters |
| **NAS** | syn | Synology DS1621+ with 10GbE for high-speed storage |
| **Home Automation** | pve-tc1 | ThinkCentre running dedicated Home Assistant |
| **Network** | rtr | UniFi Dream Machine Pro with 10GbE uplinks |

### Infrastructure Philosophy

**Hybrid Approach**:
- **MS-A2**: Optimized for Docker workloads with GPU passthrough
- **core.rsdn.io**: Dedicated to Kubernetes experimentation and development
- **Specialization**: Each host optimized for specific workload types

### Domain and DNS

- **Primary Domain:** `rsdn.io`
- **DNS Provider:** Cloudflare
- **SSL/TLS:** Let's Encrypt wildcard certificates via Traefik
- **Internal DNS:** Technitium (primary on syn, secondary on ctr01)
- **Ad Blocking:** Technitium DNS (built-in blocking)

## Repository Structure

All infrastructure is managed as code across multiple GitLab repositories:

| Repository | Purpose | Status |
|------------|---------|--------|
| [stetter-homelab/homelab-docs](https://gitlab.com/stetter-homelab/homelab-docs) | This documentation site | ✅ Active |
| [stetter-homelab/vm-platform](https://gitlab.com/stetter-homelab/vm-platform) | Packer, OpenTofu, and Ansible for VM provisioning | ✅ Active |
| [stetter-homelab/k8s-platform](https://gitlab.com/stetter-homelab/k8s-platform) | NixOS-based Kubernetes cluster management | ✅ Active |
| [stetter-homelab/talos-platform](https://gitlab.com/stetter-homelab/talos-platform) | CLI-based Talos Linux cluster management | ✅ Active |
| [stetter-homelab/talos-terraform-poc](https://gitlab.com/stetter-homelab/talos-terraform-poc) | Terraform provider approach for Talos | 🔄 Development |
| [stetter-homelab/compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) | Docker Compose stacks (multiple repos) | ✅ Active |

### Active Projects Summary

- **Docker Platform**: Stateful services on ctr01 (MS-A2)
- **Kubernetes Development**: Multiple clusters on core.rsdn.io
- **Talos Linux**: Two parallel approaches (CLI vs Terraform)
- **Security Testing**: Kali Linux environment on sec01

## Getting Started

New to the homelab? Start here:

1. **[Architecture Overview](architecture/index.md)** - Understand the overall system design
2. **[Hardware Inventory](architecture/hardware.md)** - Know what hardware is running
3. **[Network Topology](architecture/network.md)** - Understand the network layout
4. **[Service Catalog](services/index.md)** - Find the service you need

## Contributing

All documentation lives in the [stetter-homelab/docs](https://gitlab.com/stetter-homelab/docs) repository. To make changes:

1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Submit a merge request

See the [Runbooks](runbooks/index.md) section for operational procedures and standards.
