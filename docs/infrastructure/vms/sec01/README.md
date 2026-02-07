# sec01 - Kali Linux Security Testing VM

Comprehensive security testing virtual machine with GUI tools accessible via X11 forwarding.

## Overview

**sec01** is a Kali Linux-based security testing VM designed for penetration testing, vulnerability assessment, and security research within the homelab environment.

### Key Features

- **Headless Kali Linux** base template for optimal performance
- **GUI security tools** accessible via X11 forwarding (SSH -X)
- **High-performance storage** via 10G NFS for large datasets
- **Dual network interfaces** for management and storage traffic
- **Evidence collection workspace** with proper retention procedures

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        sec01 VM                            │
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │  Headless Kali  │           │    GUI Tools via X11   │  │
│  │  - CLI tools    │  SSH -X   │  - Burp Suite Pro      │  │
│  │  - Frameworks   │ ◄────────►│  - Wireshark          │  │
│  │  - Scripts      │           │  - OWASP ZAP           │  │
│  └─────────────────┘           └─────────────────────────┘  │
│           │                             │                   │
│           ▼                             ▼                   │
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │   Workspace     │           │    Evidence Storage     │  │
│  │  ~/workspace    │           │  /mnt/synology/sec01   │  │
│  │  /opt/pentest   │           │  (NFS 10G network)     │  │
│  └─────────────────┘           └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Specifications

| Component | Specification |
|-----------|--------------|
| **OS** | Kali Linux 2024.x (headless) |
| **vCPUs** | 4 cores |
| **RAM** | 12 GB |
| **Disk** | 120 GB (local SSD) |
| **Network** | Dual NIC (management + storage) |
| **Storage** | 10G NFS for evidence/datasets |

### Network Configuration

| Interface | Network | IP Address | Purpose |
|-----------|---------|------------|---------|
| eth0 | 192.168.1.0/24 | 192.168.1.25 | Management/SSH/X11 |
| eth1 | 10.0.10.0/24 | 10.0.10.25 | High-speed NFS storage |

## Quick Start

### 1. Connect via SSH with X11 Forwarding

=== "macOS (with XQuartz)"

    ```bash
    # Install XQuartz first (see x11-forwarding.md)
    ssh -X stetter@192.168.1.25

    # Test X11 forwarding
    xclock
    ```

=== "Linux"

    ```bash
    # Enable X11 forwarding
    ssh -X stetter@192.168.1.25

    # Test X11 forwarding
    xeyes
    ```

### 2. Launch Security Tools

```bash
# GUI tools (via X11 forwarding)
burpsuite &
wireshark &
zaproxy &

# CLI tools (direct terminal)
nmap -sV target.example.com
gobuster dir -u http://target.example.com -w /usr/share/wordlists/dirb/big.txt
```

### 3. Set Up Workspace

```bash
# Create engagement workspace
mkdir -p ~/workspace/$(date +%Y-%m-%d)-client-assessment
cd ~/workspace/$(date +%Y-%m-%d)-client-assessment

# Initialize evidence collection
mkdir -p {recon,scans,screenshots,payloads,reports}

# Mount NFS for large files
sudo mount -t nfs 10.0.10.10:/volume1/sec01 /mnt/synology/sec01
```

## Pre-installed Tools

### Command Line Tools
- **Network**: nmap, masscan, zmap, unicornscan
- **Web Apps**: gobuster, ffuf, wfuzz, sqlmap, nikto
- **Exploitation**: metasploit-framework, searchsploit, social-engineer-toolkit
- **Wireless**: aircrack-ng, reaver, hostapd, dnsmasq
- **Forensics**: autopsy, volatility, binwalk, foremost

### GUI Tools (X11 Required)
- **Web App Testing**: Burp Suite Professional, OWASP ZAP
- **Network Analysis**: Wireshark, Ettercap
- **Vulnerability Scanning**: Greenbone/OpenVAS, Nessus (if licensed)
- **Exploitation**: Armitage (Metasploit GUI), Cobalt Strike (if licensed)
- **Forensics**: Autopsy, Ghidra

## Storage and Evidence Handling

### Local Storage (`/opt/pentest`)
- Tool configurations and custom scripts
- Temporary working files
- Engagement notes and documentation

### NFS Storage (`/mnt/synology/sec01`)
- Large datasets and wordlists
- Evidence collections and artifacts
- Report templates and deliverables
- VM snapshots and backups

### Best Practices
- **Evidence integrity**: Use checksums for all collected evidence
- **Data retention**: Follow engagement-specific retention policies
- **Secure disposal**: Use secure deletion for sensitive data
- **Backup strategy**: Daily snapshots during active engagements

## Common Workflows

### 1. External Penetration Test

```bash
# 1. Reconnaissance
mkdir ~/workspace/client-external-$(date +%Y%m%d)
cd ~/workspace/client-external-$(date +%Y%m%d)

# 2. Network discovery
nmap -sn target-range > recon/live-hosts.txt
nmap -sV -sC -oA scans/full-scan target-range

# 3. Web application testing (GUI)
burpsuite &
# Configure proxy, spider target applications

# 4. Vulnerability assessment
nikto -h target-web-app -o scans/nikto-results.txt
```

### 2. Internal Network Assessment

```bash
# 1. Network enumeration
netdiscover -r 192.168.10.0/24
nmap -sV -sC -oA scans/internal-full 192.168.10.0/24

# 2. SMB enumeration
enum4linux target-host
smbclient -L target-host

# 3. Credential testing
crackmapexec smb 192.168.10.0/24 -u userlist -p passlist
```

### 3. Wireless Security Assessment

```bash
# 1. Monitor mode setup
airmon-ng start wlan0

# 2. Network discovery
airodump-ng wlan0mon

# 3. WPS testing
reaver -i wlan0mon -b [BSSID] -vv
```

## Performance Optimization

### X11 Forwarding Performance

```bash
# Use compression for slow connections
ssh -X -C stetter@192.168.1.25

# Enable trusted X11 forwarding (local network only)
ssh -Y stetter@192.168.1.25

# Optimize X11 forwarding for graphics-heavy tools
export DISPLAY=:10.0
```

### Resource Management

```bash
# Monitor resource usage
htop
iotop

# Adjust tool memory usage
# Burp Suite: -Xmx4g (in user.sh)
# Wireshark: limit capture buffer size
# Metasploit: adjust database settings
```

## Security Considerations

### Network Isolation
- **Management traffic**: Isolated on 192.168.1.0/24
- **Storage traffic**: Dedicated 10G network (10.0.10.0/24)
- **Target networks**: Use VPN or additional interfaces as needed

### Access Control
- **SSH key authentication** only (no password login)
- **Sudo access** for tool execution and system management
- **Firewall rules** to restrict unnecessary services

### Data Protection
- **Encryption at rest** for sensitive evidence (LUKS/eCryptfs)
- **Encrypted NFS** for evidence storage
- **Secure communications** via SSH/VPN only

## Related Documentation

- [X11 Forwarding Setup Guide](x11-forwarding.md) - Complete setup for macOS and Linux
- [Security Tools Reference](security-tools.md) - Detailed tool documentation
- [Workspace Organization Guide](workspace-guide.md) - Evidence handling and workflows
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [VM Lifecycle Management](../../../runbooks/vm-lifecycle.md) - VM management procedures

## Support

For VM provisioning and management issues:
- **Repository**: [vm-platform](https://gitlab.com/stetter-homelab/vm-platform)
- **Infrastructure docs**: [VM Platform](../../vm-platform.md)

For tool-specific questions:
- **Kali Documentation**: [docs.kali.org](https://docs.kali.org)
- **Tool manpages**: `man toolname` or `toolname --help`