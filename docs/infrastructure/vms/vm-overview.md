# Virtual Machine Overview

Comprehensive overview of all virtual machines in the Stetter Homelab.

## VM Inventory

| VM Name | Purpose | OS | vCPUs | RAM | Disk | Management IP | Status |
|---------|---------|-----|-------|-----|------|---------------|--------|
| **ctr01** | Docker host | Debian 13 | 10 | 24GB | 100GB | 192.168.1.20 | ✅ Active |
| **dev01** | Development/bastion | Ubuntu 24.04 | 4 | 8GB | 50GB | 192.168.1.21 | ✅ Active |
| **sec01** | Security testing | Kali Linux | 4 | 12GB | 120GB | 192.168.1.25 | 🚧 In Development |

## VM Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                Proxmox Hypervisor                                  │
│                              pve-ms-a2.rsdn.io                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │      ctr01      │  │      dev01      │  │             sec01                   │ │
│  │  Docker Host    │  │ Dev/Bastion     │  │       Security Testing             │ │
│  │                 │  │                 │  │                                     │ │
│  │  • Traefik      │  │  • Development  │  │  • Penetration Testing             │ │
│  │  • Monitoring   │  │    Environment  │  │  • Vulnerability Assessment        │ │
│  │  • Media Stack  │  │  • Build Tools  │  │  • Security Research               │ │
│  │  • Home Asst.   │  │  • Git Repos    │  │  • X11 GUI Tools                   │ │
│  │                 │  │                 │  │                                     │ │
│  │  RTX2000E ADA   │  │                 │  │                                     │ │
│  │  (GPU Pass.)    │  │                 │  │                                     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────────────┘ │
│           │                     │                            │                     │
└───────────┼─────────────────────┼────────────────────────────┼─────────────────────┘
            │                     │                            │
    ┌───────▼─────────────────────▼────────────────────────────▼──────────┐
    │                    Network Infrastructure                           │
    │  • Management Network: 192.168.1.0/24                              │
    │  • Storage Network: 10.0.10.0/24 (10G dedicated)                   │
    │  • NFS: Synology DS1823xs+ (10.0.10.10)                           │
    └─────────────────────────────────────────────────────────────────────┘
```

## VM Categories

### Production Services (ctr01)
**Purpose**: Hosts critical homelab services and applications

- **Container Runtime**: Docker with compose stacks
- **Services**: Traefik, Prometheus, Grafana, Home Assistant, Media Stack
- **GPU Acceleration**: NVIDIA RTX2000E ADA for AI/ML workloads
- **Storage**: NFS-mounted data, local SSD for container runtime
- **Networking**: Dual NIC for management and high-speed storage

[View ctr01 Details →](../../runbooks/vm-lifecycle.md#current-vms)

### Development (dev01)
**Purpose**: Development environment and homelab bastion host

- **Role**: Primary development workstation and jump host
- **Tools**: Development environments, build tools, Git repositories
- **Access**: SSH gateway for secure homelab access
- **Resources**: Moderate allocation for development workflows

[View dev01 Details →](../../runbooks/vm-lifecycle.md#current-vms)

### Security Testing (sec01)
**Purpose**: Dedicated security research and penetration testing

- **Operating System**: Kali Linux with headless optimization
- **Tools**: Comprehensive security testing toolkit
- **GUI Access**: X11 forwarding for graphical security tools
- **Evidence Storage**: Dedicated NFS storage for assessment data
- **Network Isolation**: Separate network segments for testing

[View sec01 Details →](sec01/README.md)

## Infrastructure Details

### Hypervisor Platform
- **Host**: pve-ms-a2.rsdn.io (Proxmox 8.x)
- **Management**: Proxmox Web UI at https://pve-ms-a2.rsdn.io:8006
- **Hardware**: Intel-based server with GPU passthrough capabilities

### Network Configuration

#### Management Network (192.168.1.0/24)
- **Purpose**: VM management, SSH access, web interfaces
- **Gateway**: 192.168.1.1 (UniFi Dream Machine)
- **DNS**: 192.168.1.4 (Pi-hole)
- **DHCP Range**: 192.168.1.100-199 (static assignments for VMs)

#### Storage Network (10.0.10.0/24)
- **Purpose**: High-speed storage traffic (NFS, backups)
- **Bandwidth**: 10 Gigabit direct connection
- **NFS Server**: Synology DS1823xs+ (10.0.10.10)
- **Performance**: Optimized for large file transfers and evidence storage

### Storage Architecture

#### VM Local Storage
- **Type**: Local SSD storage on Proxmox
- **Usage**: OS, applications, temporary files
- **Performance**: High IOPS for system responsiveness

#### NFS Shared Storage
- **Server**: Synology DS1823xs+ NAS
- **Access**: 10G network for high throughput
- **Usage**: Persistent data, media files, backups, evidence storage
- **Redundancy**: RAID 6 configuration with hot spare

## VM Management

### Provisioning
VMs are provisioned using infrastructure-as-code:

- **Templates**: Built with Packer (golden images)
- **Provisioning**: OpenTofu for VM creation and configuration
- **Configuration**: Ansible for post-deployment setup

### Monitoring and Maintenance
- **Monitoring**: Prometheus + Grafana for metrics
- **Log Aggregation**: Loki + Promtail for centralized logging
- **Backups**: Scheduled VM snapshots and data backups
- **Updates**: Automated security updates where appropriate

### Access Control
- **Authentication**: SSH key-based access only
- **Network Access**: VPN or local network required
- **Privilege Escalation**: sudo access for administrative tasks
- **Audit Logging**: All administrative actions logged

## Performance Characteristics

### Resource Allocation Strategy

| VM | CPU Strategy | Memory Strategy | Storage Strategy |
|----|--------------|-----------------|------------------|
| ctr01 | High allocation (production services) | High allocation (container overhead) | Local + NFS hybrid |
| dev01 | Moderate allocation (development tasks) | Moderate allocation (IDE/tools) | Primarily local |
| sec01 | Moderate allocation (security tools) | High allocation (analysis tools) | Local + NFS evidence |

### Network Performance

| Traffic Type | Expected Throughput | Optimization |
|--------------|-------------------|--------------|
| Management SSH | 1-10 Mbps | Low latency priority |
| X11 Forwarding | 10-100 Mbps | Compression enabled |
| NFS Storage | 1-10 Gbps | Dedicated 10G network |
| Container Registry | 100 Mbps - 1 Gbps | Cached locally |

## Security Considerations

### Network Security
- **Firewall**: iptables rules on each VM
- **Network Segmentation**: VLANs for different traffic types
- **VPN Access**: Required for external access to management interfaces
- **SSH Hardening**: Key-only authentication, custom ports

### Data Security
- **Encryption**: Full disk encryption for sensitive VMs
- **Evidence Handling**: Secure chain of custody for sec01
- **Backup Encryption**: Encrypted backups for all persistent data
- **Access Logging**: Comprehensive audit trails

### Compliance Considerations
- **Evidence Retention**: Defined policies for security assessment data
- **Data Classification**: Clear classification of homelab vs. assessment data
- **Secure Disposal**: Proper wiping of decommissioned storage

## Capacity Planning

### Current Utilization

| Resource | ctr01 | dev01 | sec01 | Total Used | Host Capacity | Available |
|----------|-------|-------|-------|------------|---------------|-----------|
| vCPUs | 10 | 4 | 4 | 18 cores | 32 cores | 14 cores |
| RAM | 24GB | 8GB | 12GB | 44GB | 128GB | 84GB |
| Storage | 100GB | 50GB | 120GB | 270GB | 2TB | 1730GB |

### Growth Planning
- **Additional VMs**: Capacity for 2-3 additional VMs
- **Seasonal Scaling**: Ability to temporarily increase allocations
- **Disaster Recovery**: Resources reserved for DR scenarios

## Disaster Recovery

### Backup Strategy
- **VM Snapshots**: Nightly snapshots retained for 7 days
- **Data Backups**: Critical data backed up to offsite storage
- **Configuration Backup**: Infrastructure code in Git repositories

### Recovery Procedures
- **VM Recovery**: Restore from snapshots or rebuild from templates
- **Data Recovery**: Restore from NFS snapshots or offsite backups
- **Infrastructure Recovery**: Redeploy using stored IaC configurations

### Testing
- **Regular Testing**: Monthly recovery drills for critical systems
- **Documentation**: Detailed recovery procedures documented and tested
- **Communication**: Clear escalation and communication procedures

## Development Roadmap

### Planned VMs

| VM Name | Purpose | Timeline | Dependencies |
|---------|---------|----------|--------------|
| test01 | CI/CD runners | Q2 2025 | Additional storage |
| k8s-master | Kubernetes control plane | Q3 2025 | Network expansion |
| k8s-worker-* | Kubernetes workers | Q3 2025 | Hardware upgrade |

### Infrastructure Improvements
- **GPU Expansion**: Additional GPU passthrough for AI workloads
- **Storage Expansion**: Additional NFS capacity for growing datasets
- **Network Upgrades**: 25G/40G network for enhanced performance

## Related Documentation

- [VM Platform Overview](../vm-platform.md) - Infrastructure-as-code implementation
- [VM Lifecycle Management](../../runbooks/vm-lifecycle.md) - Operational procedures
- [Hardware Inventory](../../architecture/hardware.md) - Physical infrastructure
- [Network Topology](../../architecture/network.md) - Network configuration
- [Backup and Recovery](../../runbooks/backup-restore.md) - DR procedures

## Quick Reference

### SSH Access
```bash
# Standard access
ssh stetter@192.168.1.20  # ctr01
ssh stetter@192.168.1.21  # dev01
ssh stetter@192.168.1.25  # sec01

# With X11 forwarding (for sec01)
ssh -X stetter@192.168.1.25
```

### Management URLs
- **Proxmox**: https://pve-ms-a2.rsdn.io:8006
- **Synology NAS**: https://10.0.10.10:5001
- **VM Monitoring**: https://grafana.rsdn.io/d/vm-overview

### Common Operations
```bash
# Check VM status on Proxmox host
ssh pve-ms-a2 'qm list'

# VM power operations
ssh pve-ms-a2 'qm start 100'   # Start VM ID 100
ssh pve-ms-a2 'qm stop 100'    # Graceful stop
ssh pve-ms-a2 'qm reset 100'   # Hard reset
```