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

    Proxmox guests with OpenTofu and Ansible; the Mac Studio's LaunchDaemons

    [:octicons-arrow-right-24: Infrastructure Overview](infrastructure/index.md)

-   :material-docker:{ .lg .middle } __Stacks__

    ---

    Docker Compose stacks on ctr01 and the Synology

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

## Infrastructure at a Glance

| Component | Host | Description |
|-----------|------|-------------|
| **Hypervisor** | nexus | Minisforum MS-A2, Ryzen 9 9955HX, 64 GB, Proxmox 9.2 |
| **Docker host** | ctr01 | Debian 13 VM on nexus with an RTX 2000E Ada: every Compose stack and Traefik |
| **AI server** | Mac Studio | M5 Max, 64 GB: Ollama (MLX), Open WebUI, Hermes agent |
| **Home automation** | pve-tc1 | ThinkCentre running Home Assistant OS |
| **NAS** | syn | Synology DS1621+, 10GbE to nexus, primary DNS, GitLab VM |
| **Network** | rtr | UniFi Dream Machine Pro |
| **Clients** | | MacBook Air M4, iPad, iPhone |

### What Changed in 2026

- **Local AI.** A Mac Studio runs Qwen3.8 27B for the Hermes agent and Open WebUI; ctr01's GPU runs `gpt-oss-ha:20b` for Home Assistant voice. See [Local AI](architecture/ai.md).
- **No public ingress.** Since 2026-11-02 the UDM Pro forwards no ports and every Traefik router is on `websecure` (443). Admin UIs are behind Authentik. See [Network Topology](architecture/network.md#reverse-proxy-traefik).
- **Tailscale** subnet routing with split DNS is the way in from outside; people who need a service are invited to the tailnet. The UDM Pro's WireGuard VPN stays on as a backup.
- **GitLab** moved from a container on ctr01 to a VM on the Synology.
- **Retired:** the MacBook Pros, core.rsdn.io and its Kubernetes/Talos clusters, gpu.rsdn.io, n8n, Whishper, vLLM.

### Domain and DNS

- **Internal:** `*.rsdn.io` → CNAME `rprx.rsdn.io` (ctr01), served by Technitium (primary on syn, secondary on ctr01)
- **Public:** Cloudflare DNS. `stetter.io` is served by Cloudflare Workers Static Assets (not the homelab); nothing in the homelab is internet-facing
- **TLS:** Let's Encrypt wildcard via Traefik (Cloudflare DNS-01)

## Repositories

| Repository | Purpose |
|------------|---------|
| [homelab-docs](https://github.com/johnstetter/homelab-docs) | This site (GitHub) |
| [vm-platform](https://gitlab.com/stetter-homelab/vm-platform) | OpenTofu + Ansible for Proxmox guests and hosts |
| [compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) | One repo per Docker Compose stack on ctr01 |
| [ci-templates](https://gitlab.com/stetter-homelab/ci-templates) | Shared GitLab CI templates |
| [mac-config](https://gitlab.com/stetter-homelab/mac-config) | Both Macs: Brewfile, dotfiles, Studio LaunchDaemons |
| [home-assistant-config](https://gitlab.com/stetter-homelab/home-assistant-config) | Home Assistant configuration |

## Getting Started

New to the homelab? Start here:

1. **[Architecture Overview](architecture/index.md)** - Understand the overall system design
2. **[Hardware Inventory](architecture/hardware.md)** - Know what hardware is running
3. **[Network Topology](architecture/network.md)** - Understand the network layout
4. **[Service Catalog](services/index.md)** - Find the service you need
5. **[Local AI](architecture/ai.md)** - How inference is split between the Studio and ctr01

## Contributing

All documentation lives in [johnstetter/homelab-docs](https://github.com/johnstetter/homelab-docs) on GitHub, whose Actions workflow publishes this site to GitHub Pages. To make changes:

1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Open a pull request

See the [Runbooks](runbooks/index.md) section for operational procedures and standards.
