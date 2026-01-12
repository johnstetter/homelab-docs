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

The Stetter Homelab runs on a combination of Proxmox VE virtualization, Docker containers, and a Synology NAS for storage and supplementary services.

### Core Components

| Component | Host | Description |
|-----------|------|-------------|
| **Proxmox VE** | pve-ms-a2 | Primary hypervisor running on Minisforum MS-A2 |
| **Docker Host** | ctr01 | Debian 13 VM hosting all primary Docker stacks |
| **Development** | dev01 | Ubuntu 24.04 VM for development and bastion access |
| **NAS** | syn | Synology DS1621+ for storage and secondary services |
| **Home Automation** | pve-tc1 | ThinkCentre running Home Assistant |
| **Network** | rtr | UniFi Dream Machine Pro |

### Domain and DNS

- **Primary Domain:** `rsdn.io`
- **DNS Provider:** Cloudflare
- **SSL/TLS:** Let's Encrypt wildcard certificates via Traefik
- **Internal DNS:** Technitium (primary on syn, secondary on ctr01)
- **Ad Blocking:** Pi-hole on Synology

## Repository Structure

All infrastructure is managed as code across multiple GitLab repositories:

| Repository | Purpose |
|------------|---------|
| [stetter-homelab/homelab-docs](https://gitlab.com/stetter-homelab/homelab-docs) | This documentation site |
| [stetter-homelab/vm-platform](https://gitlab.com/stetter-homelab/vm-platform) | Packer, OpenTofu, and Ansible for VM provisioning |
| [stetter-homelab/k8s-platform](https://gitlab.com/stetter-homelab/k8s-platform) | Kubernetes cluster configuration |
| [stetter-homelab/compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) | Docker Compose stacks (one repo per stack) |

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
