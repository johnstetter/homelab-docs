# Architecture Overview

The Stetter Homelab is designed around principles of reproducibility, automation, and maintainability. This section provides a high-level overview of the system architecture.

## Design Principles

1. **Infrastructure as Code** - All infrastructure is defined in code and version controlled
2. **Containerization** - Services run in Docker containers for consistency and portability
3. **Centralized Logging** - All logs flow to Loki for unified observability
4. **Automated Deployments** - GitLab CI/CD pipelines handle deployments
5. **Secure by Default** - Internal services behind Traefik with Let's Encrypt SSL

## System Architecture Diagram

```mermaid
graph TB
    subgraph Internet
        CF[Cloudflare DNS]
        LE[Let's Encrypt]
    end

    subgraph Network["Management Network (192.168.1.0/24)"]
        RTR[UniFi Dream Machine Pro<br/>192.168.1.1]

        subgraph MS_A2["pve-ms-a2 (192.168.1.12)"]
            CTR01[ctr01 - Docker Host<br/>192.168.1.20]
            DEV01[dev01 - Dev/Bastion<br/>192.168.1.21]
            SEC01[sec01 - Security Testing<br/>192.168.1.25]
        end

        subgraph CORE["core.rsdn.io (192.168.1.5)"]
            K8S_PROD[Production K8s Cluster<br/>VMs 106-115]
            TALOS_DEV[Talos Development<br/>VMs 126-131]
            K8S_DEV[NixOS/Terraform K8s<br/>VMs 120-125]
        end

        SYN[Synology DS1621+<br/>192.168.1.4]
        TC1[pve-tc1 - Home Assistant<br/>192.168.1.11]
    end

    subgraph Storage["Storage Network (10.0.10.0/24)"]
        SYN10G[Synology 10GbE<br/>10.0.10.4]
        CTR01_10G[ctr01 Storage<br/>10.0.10.20]
    end

    CF --> RTR
    LE --> CTR01
    RTR --> CTR01
    RTR --> SYN
    RTR --> TC1
    RTR --> CORE
    CTR01 <--> SYN
    DEV01 --> CTR01
    
    %% 10GbE Storage Network
    SYN10G <--> CTR01_10G
    CTR01 -.-> CTR01_10G
    SYN -.-> SYN10G

    %% K8s Clusters
    CORE --> SYN
```

## Virtualization Layer

**Hybrid Proxmox Architecture** with specialized workload separation:

### MS-A2 Hypervisor (Docker-focused)
**Proxmox VE** on Minisforum MS-A2 optimized for Docker workloads:

- **ctr01** - Docker host with GPU passthrough (Debian 13)
- **dev01** - Development and bastion VM (Ubuntu 24.04) 
- **sec01** - Security testing environment (Kali Linux)

### core.rsdn.io Hypervisor (K8s-focused)
**Proxmox VE** on Dell PowerEdge optimized for Kubernetes experimentation:

- **Production K8s** - 7-VM cluster (3 control + 4 workers)
- **Talos Development** - 6-VM cluster for Talos Linux testing
- **NixOS/Terraform K8s** - 6-VM development environment
- **Utility VMs** - Testing and ansible infrastructure

### Dedicated Hosts
- **pve-tc1** - ThinkCentre running dedicated Home Assistant

## Container Orchestration

Docker Compose is used for all container workloads. Stacks are organized by function:

- **Core Services** - Traefik reverse proxy, Vault secrets management
- **Monitoring** - Prometheus, Grafana, Loki, Jaeger
- **Media** - Plex, Sonarr, Radarr, and the *arr stack
- **AI/ML** - Ollama, Open-WebUI, Whisper
- **Development** - GitLab, code-server, IT-Tools

See [Stacks Overview](../stacks/index.md) for complete details.

## Storage Architecture

```mermaid
graph LR
    subgraph Synology["Synology DS1621+"]
        VOL1["Volume 1<br/>42TB SHR"]
        E10G["E10G21-F2<br/>Dual 10GbE"]
    end

    subgraph NFS["NFS Shares"]
        DOCKER["/volume1/docker"]
        MEDIA["/volume1/media"]
        K8S["/volume1/k8s"]
        SECURITY["/volume1/security"]
        BACKUP["/volume1/backups"]
    end

    subgraph Networks["Storage Networks"]
        NET10G["10.0.10.0/24<br/>10GbE MTU 9000"]
        NET1G["192.168.1.0/24<br/>1GbE"]
    end

    subgraph Mounts["Host Mounts"]
        MS_A2["MS-A2 VMs<br/>/mnt/synology/*"]
        CORE["core.rsdn.io VMs<br/>/mnt/k8s/*"]
    end

    VOL1 --> DOCKER
    VOL1 --> MEDIA
    VOL1 --> K8S
    VOL1 --> SECURITY
    VOL1 --> BACKUP
    
    DOCKER --> NET10G
    MEDIA --> NET10G
    SECURITY --> NET10G
    K8S --> NET1G
    
    NET10G --> MS_A2
    NET1G --> CORE
```

### Storage Tiers

| Tier | Network | Performance | Purpose |
|------|---------|-------------|---------|
| **10GbE Storage** | 10.0.10.0/24 | ~1GB/s | MS-A2 Docker/media workloads |
| **1GbE Storage** | 192.168.1.0/24 | ~100MB/s | core.rsdn.io K8s clusters |
| **Local NVMe** | VM hosts | ~2GB/s | VM disks, OS, temporary files |

## Network Architecture

See [Network Topology](network.md) for detailed network documentation.

### Key Network Segments

- **192.168.1.0/24** - Primary LAN
- **Traefik** - Reverse proxy for all HTTP/HTTPS traffic
- **Cloudflare** - External DNS and DDoS protection
- **Technitium** - Internal DNS resolution

## Security Model

### External Access

1. All external traffic routes through Cloudflare
2. Traefik handles SSL termination with Let's Encrypt wildcards
3. Sensitive services require authentication (Authentik or basic auth)

### Internal Security

1. Internal services communicate over Docker networks
2. Secrets managed via HashiCorp Vault
3. SSH access via bastion host (dev01)
4. SSH-signed commits required for all code changes

## Monitoring and Observability

The monitoring stack provides comprehensive visibility:

| Component | Purpose |
|-----------|---------|
| **Prometheus** | Metrics collection and alerting |
| **Grafana** | Dashboards and visualization |
| **Loki** | Log aggregation |
| **Jaeger** | Distributed tracing |
| **Node Exporter** | Host metrics |

See [Service Catalog](../services/index.md) for access URLs.

## Disaster Recovery

### Backup Strategy

- **Daily**: Database dumps, Docker volume snapshots
- **Weekly**: Full system backups to Synology HDD pool
- **Monthly**: Offsite backup verification

### Recovery Procedures

See [Troubleshooting Runbook](../runbooks/troubleshooting.md) for recovery procedures.
