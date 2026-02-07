# ctr01 - Debian Docker Host VM

High-performance Docker host with GPU acceleration for AI/ML workloads and containerized homelab services.

## Overview

**ctr01** is a Debian 13-based Docker host VM that serves as the primary container platform for the homelab infrastructure. It hosts critical services including reverse proxy, monitoring, media streaming, AI workloads, and automation tools.

### Key Features

- **GPU-accelerated containers** with NVIDIA RTX2000E ADA passthrough
- **High-performance Docker platform** with optimized container runtime
- **Dual network interfaces** for management and high-speed storage access
- **10 Gigabit NFS storage** integration for media and data persistence
- **Comprehensive service stack** including monitoring, media, and AI services
- **Hardware transcoding** for media streaming and AI inference

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   ctr01 VM                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────────────────────────┐  │
│  │     Core Services       │      │         AI/GPU Workloads                   │  │
│  │  - Traefik (Proxy)     │      │  - Ollama (LLM Server)                    │  │
│  │  - Vault (Secrets)     │      │  - Whisper (Speech-to-Text)               │  │
│  │  - Prometheus/Grafana  │      │  - Frigate NVR (Object Detection)         │  │
│  │  - GitLab CE           │      │  - Plex (Hardware Transcoding)            │  │
│  └─────────────────────────┘      └─────────────────────────────────────────────┘  │
│             │                                      │                              │
│             ▼                                      ▼                              │
│  ┌─────────────────────────┐      ┌─────────────────────────────────────────────┐  │
│  │    Media & Content      │      │         NVIDIA RTX2000E ADA                │  │
│  │  - Plex Media Server   │      │  - 16GB VRAM                               │  │
│  │  - Sonarr/Radarr       │      │  - NVENC/NVDEC (Video)                    │  │
│  │  - SABnzbd             │      │  - CUDA/TensorRT (AI)                     │  │
│  │  - Jellyfin/Emby       │      │  - Hardware Acceleration                   │  │
│  └─────────────────────────┘      └─────────────────────────────────────────────┘  │
│             │                                      │                              │
│             ▼                                      ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                        Storage & Networking                                 │  │
│  │  Management: 192.168.1.20 (1G) ◄──────────► Storage: 10.0.10.20 (10G)    │  │
│  │  Local SSD: 100GB (OS/Containers) ◄────────► NFS: Synology (Media/Data)   │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Specifications

| Component | Specification |
|-----------|--------------|
| **OS** | Debian 13 (Trixie) |
| **vCPUs** | 10 cores |
| **RAM** | 24 GB |
| **Disk** | 100 GB (local SSD) |
| **GPU** | NVIDIA RTX2000E ADA 16GB (passthrough) |
| **Network** | Dual NIC (management + 10G storage) |
| **Hypervisor** | Proxmox VE on pve-ms-a2 |

!!! note "Specification Sources"
    Current specifications reflect actual VM allocation. Some documentation files show different values due to past changes or planning documents.

### Network Configuration

| Interface | Network | IP Address | Purpose |
|-----------|---------|------------|---------|
| eth0 | 192.168.1.0/24 | 192.168.1.20 | Management/SSH/Web Services |
| eth1 | 10.0.10.0/24 | 10.0.10.20 | High-speed NFS storage access |

### GPU Configuration

| Component | Specification |
|-----------|--------------|
| **GPU Model** | NVIDIA RTX2000E ADA |
| **VRAM** | 16 GB GDDR6 |
| **CUDA Cores** | 2816 |
| **RT Cores** | 3rd Gen (22 cores) |
| **Tensor Cores** | 4th Gen (88 cores) |
| **PCI Address** | 0000:01:00 (passthrough from host) |

## Quick Start

### 1. SSH Access and Container Management

```bash
# SSH access to ctr01
ssh stetter@192.168.1.20

# Or using SSH config alias
ssh ctr01

# Quick container status check
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 2. Docker Stack Operations

```bash
# Navigate to stack directories
cd /opt/stacks/

# List all stacks
ls -la /opt/stacks/
# core/  monitoring/  media/  ai/  frigate/  etc.

# Start/stop/restart stacks
cd /opt/stacks/monitoring
docker compose up -d     # Start stack
docker compose down      # Stop stack
docker compose restart   # Restart stack

# View logs
docker compose logs -f prometheus
docker compose logs --tail 100 grafana
```

### 3. GPU Status and Utilization

```bash
# Check GPU status
nvidia-smi

# Monitor GPU usage in real-time
watch -n 1 nvidia-smi

# Check GPU usage by container
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# Docker GPU test
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

## Docker Platform Configuration

### Docker Engine Setup

**System Configuration:**
- **Docker version**: Latest stable from Docker CE repository
- **Storage driver**: overlay2 on local SSD
- **Runtime**: nvidia-docker2 for GPU container support
- **Logging**: JSON file driver with rotation
- **Network**: Bridge networking with custom networks

**Docker Daemon Configuration** (`/etc/docker/daemon.json`):
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-runtime": "runc",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
```

### Stack Organization

**Stack Structure** (`/opt/stacks/`):
```
/opt/stacks/
├── core/               # Traefik, Vault
├── monitoring/         # Prometheus, Grafana, Loki
├── management/         # Portainer, Dozzle, Semaphore
├── media-servers/      # Plex, Jellyfin, Emby
├── media/             # Sonarr, Radarr, SABnzbd
├── ai/                # Ollama, OpenWebUI, n8n
├── frigate/           # Frigate NVR, MQTT
├── dev-tools/         # code-server, Flame, IT-Tools
├── gitlab/            # GitLab CE
└── automation/        # Watchtower, scripts
```

### Network Architecture

**Docker Networks:**
- **traefik_default**: Main reverse proxy network
- **monitoring_default**: Isolated monitoring stack
- **media_default**: Media services with VPN integration
- **ai_default**: AI/ML services with GPU access

**Service Discovery:**
- **Traefik labels** for automatic routing
- **Docker DNS** for inter-container communication
- **External networks** for cross-stack communication

## GPU Acceleration and AI Workloads

### NVIDIA Driver Configuration

**Driver Stack:**
- **NVIDIA Driver**: Latest production driver (535+)
- **CUDA Runtime**: 12.0+ for container compatibility
- **Docker NVIDIA Runtime**: nvidia-docker2 integration
- **Container Toolkit**: NVIDIA Container Toolkit

**Verification Commands:**
```bash
# Check driver installation
lsmod | grep nvidia
cat /proc/driver/nvidia/version

# Test CUDA functionality
nvidia-smi
nvidia-smi -q

# Container GPU access test
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### GPU-Accelerated Services

#### AI/ML Services
- **Ollama**: Local LLM inference with CUDA acceleration
- **Whisper**: Speech-to-text transcription
- **Frigate**: Real-time object detection using TensorRT

#### Media Services
- **Plex**: Hardware video transcoding (NVENC/NVDEC)
- **Jellyfin**: GPU-accelerated video processing
- **Tautulli**: Transcoding monitoring and statistics

### GPU Resource Management

**Memory Allocation:**
```bash
# Monitor GPU memory usage
nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv

# Check per-process GPU usage
nvidia-smi --query-compute-apps=pid,used_memory --format=csv

# GPU utilization over time
nvidia-smi dmon -s pucvmet
```

**Container Resource Limits:**
```yaml
# Example GPU resource allocation in compose
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Storage Configuration

### Local Storage (100GB SSD)

**Storage Allocation:**
- **OS & System**: ~15GB (Debian base system)
- **Docker Root**: ~60GB (`/var/lib/docker`)
- **Container Configs**: ~10GB (`/opt/stacks/`)
- **Logs & Cache**: ~10GB (rotated/cleaned)
- **Free Space**: ~5GB (system overhead)

**Docker Storage Optimization:**
```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a --volumes

# Monitor storage usage
df -h /var/lib/docker
du -sh /opt/stacks/*
```

### NFS Storage (10 Gigabit)

**NFS Mount Points:**
```bash
# Media storage (movies, TV, music)
/mnt/synology/media     # Read-only for media servers
/mnt/synology/downloads # Read-write for automation

# Application data
/mnt/synology/docker    # Persistent container data
/mnt/synology/backups   # Configuration backups

# Monitoring data
/mnt/synology/prometheus # Long-term metrics storage
/mnt/synology/grafana   # Dashboard configurations
```

**NFS Performance Tuning:**
```bash
# /etc/fstab NFS mount options
10.0.10.10:/volume1/docker /mnt/synology/docker nfs4 \
  rw,hard,intr,rsize=65536,wsize=65536,vers=4.1 0 0
```

## Service Management and Monitoring

### Stack Monitoring

**Prometheus Metrics:**
- **Container metrics** via cAdvisor
- **Host metrics** via Node Exporter
- **GPU metrics** via DCGM Exporter
- **Docker metrics** via Docker daemon
- **Service-specific metrics** per application

**Grafana Dashboards:**
- **Docker Host Overview**: Container and host metrics
- **GPU Utilization**: Real-time GPU monitoring
- **Service Health**: Per-stack service status
- **Storage Performance**: NFS and local storage metrics

### Log Management

**Centralized Logging:**
- **Loki** for log aggregation
- **Promtail** for log collection
- **Grafana** for log visualization and search

**Log Sources:**
- **Container logs**: All Docker service logs
- **System logs**: Host OS and Docker daemon
- **Application logs**: Service-specific logging
- **GPU logs**: NVIDIA driver and CUDA logs

### Health Monitoring

```bash
# Service health checks
curl -f http://localhost:8080/api/health  # Traefik
curl -f http://localhost:9090/-/healthy  # Prometheus
docker exec plex curl -f http://localhost:32400/web/

# Resource monitoring
docker stats --no-stream
free -h
df -h
nvidia-smi --query-gpu=utilization.gpu --format=csv
```

## Performance Optimization

### CPU and Memory

**Resource Allocation Strategy:**
- **Core services** (Traefik, Vault): Guaranteed resources
- **AI workloads** (Ollama): High CPU allocation during inference
- **Media services** (Plex): CPU for non-GPU transcoding
- **Background services**: Lower priority scheduling

**Memory Management:**
```bash
# Monitor container memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check system memory
free -h
cat /proc/meminfo
```

### Storage Performance

**Local SSD Optimization:**
- **ext4 filesystem** with noatime mount option
- **Docker overlay2** storage driver
- **Log rotation** to prevent disk space exhaustion

**NFS Performance:**
```bash
# Test NFS performance
dd if=/dev/zero of=/mnt/synology/test bs=1M count=1000
rm /mnt/synology/test

# Monitor NFS statistics
nfsstat -c
iostat -x 1
```

### GPU Performance

**GPU Optimization:**
- **GPU memory management** for concurrent workloads
- **CUDA stream optimization** for AI inference
- **NVENC/NVDEC utilization** for media transcoding

**Performance Monitoring:**
```bash
# GPU performance metrics
nvidia-smi dmon -s pucvmet -c 1
nvidia-smi -q -x | grep -E "utilization|temperature"

# Application GPU usage
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
```

## Security Considerations

### Container Security

**Runtime Security:**
- **Non-root containers** where possible
- **Read-only filesystems** for stateless services
- **Resource limits** to prevent DoS
- **Network segmentation** between stacks

**Image Security:**
- **Official images** preferred
- **Vulnerability scanning** via Docker Scout
- **Pinned image versions** for stability
- **Regular image updates** via Watchtower

### Network Security

**Docker Networks:**
- **Isolated networks** per stack
- **Traefik integration** for centralized routing
- **No direct host exposure** except Traefik
- **Internal service communication** via Docker DNS

**Access Control:**
- **SSH key authentication** only
- **Traefik middleware** for service authentication
- **Vault integration** for secret management
- **VPN required** for external access

### GPU Security

**GPU Access Control:**
- **Container-level GPU allocation**
- **Resource limits** for GPU memory
- **Driver isolation** from host system
- **Secure GPU passthrough** configuration

## Disaster Recovery and Backup

### Container Backup Strategy

**Configuration Backup:**
- **Docker Compose files** in git repository
- **Environment variables** in `.env` files
- **Volume mounts** to NFS for persistence

**Data Backup:**
- **NFS snapshots** for application data
- **Database exports** for critical data
- **Configuration exports** via automation

### Recovery Procedures

**Stack Recovery:**
```bash
# Restore stack from backup
cd /opt/stacks/monitoring
git pull origin main
docker compose down
docker compose pull
docker compose up -d
```

**Complete VM Recovery:**
```bash
# From dev01 or management host
cd ~/projects/vm-platform
devbox shell
tofu apply -replace="proxmox_vm_qemu.ctr01"
ansible-playbook ansible/site.yml -l ctr01
```

## Related Documentation

- [ctr01 Service Stacks](../../../stacks/ctr01.md) - Detailed service documentation
- [VM Platform Overview](../../vm-platform.md) - Infrastructure-as-code implementation
- [VM Lifecycle Management](../../../runbooks/vm-lifecycle.md) - Operational procedures
- [GPU Troubleshooting](../../../runbooks/troubleshooting.md#gpu-issues-rtx-2000e-ada) - GPU-specific issues
- [Docker Service Guides](../../../services/index.md) - Individual service documentation

## Support

### Platform Support
- **Repository**: [vm-platform](https://gitlab.com/stetter-homelab/vm-platform)
- **Infrastructure docs**: [VM Platform](../../vm-platform.md)
- **Issue Tracking**: GitLab Issues in vm-platform repository

### Service Support
- **Service Documentation**: [Services Index](../../../services/index.md)
- **Stack Documentation**: [ctr01 Stacks](../../../stacks/ctr01.md)
- **Monitoring**: [Grafana Dashboard](https://grafana.rsdn.io)

### Quick Reference

```bash
# SSH and basic access
ssh ctr01                              # SSH access
ssh ctr01 'docker ps'                  # Quick container check
ssh ctr01 'nvidia-smi'                 # GPU status

# Stack management
cd /opt/stacks/stackname              # Navigate to stack
docker compose up -d                  # Start stack
docker compose logs -f service        # View logs
docker compose restart service        # Restart service

# System monitoring
docker stats                          # Container resource usage
nvidia-smi                           # GPU utilization
df -h                                # Disk usage
free -h                              # Memory usage

# Common directories
/opt/stacks/                         # All Docker stacks
/mnt/synology/                       # NFS mounted storage
/var/lib/docker/                     # Docker root directory
```