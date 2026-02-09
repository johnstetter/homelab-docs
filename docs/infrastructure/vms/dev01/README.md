# dev01 - Ubuntu Development and Bastion VM

Development environment and secure bastion host for homelab infrastructure management.

## Overview

**dev01** is an Ubuntu 24.04 LTS-based development VM that serves dual purposes: primary development environment for infrastructure-as-code and secure bastion host for accessing homelab resources.

### Key Features

- **Infrastructure-as-Code Development** with OpenTofu, Ansible, and Packer
- **Secure bastion host** for SSH access to homelab infrastructure
- **Development environments** managed via Devbox (Nix-based)
- **Git repository hosting** for infrastructure automation
- **Dual network interfaces** for management and development workflows

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            dev01 VM                                        │
│  ┌─────────────────────┐           ┌─────────────────────────────────────┐  │
│  │   Bastion Access    │           │      Development Environment       │  │
│  │  - SSH Gateway      │           │  - VM Platform (IaC)              │  │
│  │  - Jump Host        │  Local    │  - OpenTofu/Terraform             │  │
│  │  - Key Management   │ ◄────────►│  - Ansible Automation             │  │
│  │                     │           │  - Packer Templates               │  │
│  └─────────────────────┘           └─────────────────────────────────────┘  │
│           │                                 │                              │
│           ▼                                 ▼                              │
│  ┌─────────────────────┐           ┌─────────────────────────────────────┐  │
│  │  SSH Connections    │           │     Development Tools              │  │
│  │  to Infrastructure  │           │  - Devbox Environments             │  │
│  │  (ctr01, sec01,     │           │  - Code Editors                    │  │
│  │   Proxmox, etc.)    │           │  - Git Repositories                │  │
│  └─────────────────────┘           └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Specifications

| Component | Specification |
|-----------|--------------|
| **OS** | Ubuntu 24.04 LTS (Noble) |
| **vCPUs** | 4 cores |
| **RAM** | 16 GB |
| **Disk** | 50 GB (local SSD) |
| **Network** | Single NIC (management) |
| **Hypervisor** | Proxmox VE on pve-ms-a2 |

### Network Configuration

| Interface | Network | IP Address | Purpose |
|-----------|---------|------------|---------|
| eth0 | 192.168.1.0/24 | 192.168.1.21 | Management/SSH/Development |

## Quick Start

### 1. SSH Access (Bastion Entry Point)

```bash
# Direct SSH access to dev01
ssh stetter@192.168.1.21

# Or using SSH config alias
ssh dev01

# SSH with agent forwarding for git operations
ssh -A stetter@192.168.1.21
```

### 2. Infrastructure Development Workflow

```bash
# Enter infrastructure development environment
ssh dev01
cd ~/projects/vm-platform
devbox shell

# Infrastructure operations
tofu plan    # Plan infrastructure changes
tofu apply   # Apply infrastructure changes

# VM provisioning with Ansible
ansible-playbook ansible/site.yml -l ctr01

# Template building with Packer
cd packer/debian-docker-host
packer build -var-file=credentials.pkrvars.hcl .
```

### 3. Using as SSH Bastion/Jump Host

```bash
# Access other VMs through dev01
ssh -J dev01 stetter@192.168.1.20  # ctr01 via dev01
ssh -J dev01 stetter@192.168.1.25  # sec01 via dev01

# SSH config for jump host setup (~/.ssh/config)
Host ctr01
  HostName 192.168.1.20
  User stetter
  ProxyJump dev01

Host sec01
  HostName 192.168.1.25
  User stetter
  ProxyJump dev01
```

## Pre-installed Tools and Environments

### Development Tools (via Devbox)

**Global Tools** (available system-wide via `devbox global`):
- **lazygit** - Git TUI for repository management
- **neovim** - Advanced text editor
- **ripgrep (rg)** - Fast text search
- **fd** - Fast file finder
- **fzf** - Fuzzy finder for command line
- **bat** - Enhanced cat with syntax highlighting
- **lsd** - Modern ls replacement

**Project-Specific Tools** (per-project via `devbox shell`):
- **OpenTofu** - Infrastructure-as-code (Terraform fork)
- **Ansible** - Configuration management and automation
- **Packer** - VM template building
- **Docker** - Container runtime for testing
- **kubectl** - Kubernetes CLI (future K8s cluster management)

### Infrastructure-as-Code Stack

**VM Platform Repository** (`~/projects/vm-platform`):
- **Templates**: Packer templates for Debian, Ubuntu, Kali Linux
- **Infrastructure**: OpenTofu configurations for VM provisioning
- **Automation**: Ansible playbooks for VM configuration
- **Documentation**: Infrastructure documentation and runbooks

### Development Environment Management

**Devbox Configuration** (`devbox.json` per project):
```json
{
  "packages": [
    "terraform@1.6.6",
    "ansible@8.5.0",
    "packer@1.9.4",
    "python310@3.10.13",
    "go@1.21.4"
  ],
  "shell": {
    "init_hook": [
      "echo 'VM Platform Development Environment'",
      "terraform --version",
      "ansible --version"
    ]
  }
}
```

## Storage and Project Organization

### Local Storage (`/home/stetter`)

**Project Structure:**
```
~/projects/
├── vm-platform/           # Main IaC repository
│   ├── terraform/         # OpenTofu/Terraform configs
│   ├── ansible/          # Ansible playbooks and roles
│   ├── packer/           # VM template definitions
│   └── devbox.json       # Development environment
├── homelab-docs/         # Documentation repository
└── infrastructure-tools/ # Additional automation scripts
```

### SSH Key Management

**SSH Keys for Infrastructure Access:**
```bash
~/.ssh/
├── id_rsa              # Primary key for Git operations
├── id_rsa.pub          # Public key
├── proxmox_ed25519     # Proxmox API access key
├── deployment_key      # GitLab deployment key
└── config              # SSH configuration
```

**SSH Config Example:**
```bash
# ~/.ssh/config
Host pve-*
  User root
  IdentityFile ~/.ssh/proxmox_ed25519
  StrictHostKeyChecking no

Host ctr01
  HostName 192.168.1.20
  User stetter
  ForwardAgent yes

Host sec01
  HostName 192.168.1.25
  User stetter
  ForwardX11 yes
```

## Common Workflows

### 1. VM Provisioning and Management

```bash
# Connect to development environment
ssh dev01
cd ~/projects/vm-platform
devbox shell

# Create new VM configuration
mkdir terraform/vms/new-vm
cd terraform/vms/new-vm

# Write OpenTofu configuration
cat > main.tf << 'EOF'
resource "proxmox_vm_qemu" "new-vm" {
  name        = "new-vm"
  target_node = "pve-ms-a2"
  vmid        = 123

  cores    = 4
  memory   = 8192

  # ... rest of configuration
}
EOF

# Plan and apply infrastructure changes
tofu init
tofu plan
tofu apply

# Configure VM with Ansible
cd ../../../ansible
ansible-playbook site.yml -l new-vm
```

### 2. Template Building Workflow

```bash
# Build new Packer template
ssh dev01
cd ~/projects/vm-platform/packer
devbox shell

# Create new template (e.g., Ubuntu 24.04)
cp -r debian-docker-host ubuntu-24.04-dev
cd ubuntu-24.04-dev

# Edit template configuration
vim ubuntu-24.04.pkr.hcl

# Build template
packer init .
packer validate .
packer build -var-file=credentials.pkrvars.hcl .
```

### 3. Ansible Automation Workflow

```bash
# SSH to dev01 and enter vm-platform
ssh dev01
cd ~/projects/vm-platform/ansible
devbox shell

# Run playbooks against infrastructure
ansible-playbook site.yml                    # All hosts
ansible-playbook site.yml -l container_hosts # Just container hosts
ansible-playbook site.yml -l ctr01          # Single host

# Run specific roles or tags
ansible-playbook site.yml -l ctr01 --tags docker
ansible-playbook site.yml -l sec01 --tags security-tools

# Check inventory and connectivity
ansible all -m ping
ansible all -m setup --tree /tmp/facts
```

### 4. Development and Testing

```bash
# Test infrastructure changes locally
ssh dev01
cd ~/projects/vm-platform
devbox shell

# Validate Terraform/OpenTofu syntax
tofu fmt -recursive .
tofu validate

# Test Ansible playbooks
ansible-playbook site.yml --check --diff
ansible-playbook site.yml --limit dev01 --check

# Lint and validate configurations
ansible-lint ansible/
packer validate packer/*/
```

## Performance Optimization

### Resource Allocation

**CPU Allocation:**
- 4 vCPUs provide adequate performance for infrastructure automation
- OpenTofu operations are generally single-threaded
- Ansible parallel execution benefits from multiple cores
- Packer builds can be CPU-intensive during template creation

**Memory Usage:**
- 16 GB RAM supports multiple concurrent development environments
- Large Ansible inventories benefit from additional memory
- Packer builds may require significant RAM for VM creation
- Devbox environments use minimal overhead

### Development Environment Optimization

```bash
# Optimize shell startup with devbox
eval "$(devbox global shellenv --init-hook)"

# Use persistent shell environments
devbox shell --persistent

# Cache downloaded packages
export DEVBOX_CACHE_DIR=/home/stetter/.cache/devbox

# Git optimization for large repositories
git config --global core.preloadindex true
git config --global core.fscache true
```

### SSH Connection Optimization

```bash
# ~/.ssh/config optimizations
Host *
  ControlMaster auto
  ControlPath ~/.ssh/sockets/%r@%h-%p
  ControlPersist 600
  ServerAliveInterval 60
  ServerAliveCountMax 3
  Compression yes
```

## Security Considerations

### Bastion Host Security

**Access Control:**
- **SSH key authentication** only (no password login)
- **SSH agent forwarding** for Git operations
- **Firewall rules** restricting unnecessary ports
- **Fail2ban** protection against brute force attacks

**Audit Logging:**
- **SSH session logging** via rsyslog
- **Command history** preservation
- **Git operation tracking** in repositories
- **Ansible execution logs** for automation audit trails

### Infrastructure Security

**Secrets Management:**
- **SSH keys** stored securely in `~/.ssh/`
- **API credentials** in environment variables or Vault
- **Git repository secrets** never committed to version control
- **Proxmox credentials** in secure credential files

**Network Security:**
- **VPN required** for external access to dev01
- **Internal network access** to infrastructure hosts
- **No direct internet exposure** of management interfaces
- **Encrypted communications** for all infrastructure operations

### Development Security

**Code Security:**
- **Pre-commit hooks** for secret detection
- **Code review** requirements for infrastructure changes
- **Version control** for all configuration changes
- **Infrastructure testing** before production deployment

## Related Documentation

- [VM Platform Overview](../../vm-platform.md) - Infrastructure-as-code implementation
- [VM Lifecycle Management](../../../runbooks/vm-lifecycle.md) - Operational procedures
- [Hardware Inventory](../../../architecture/hardware.md) - Physical infrastructure
- [Network Topology](../../../architecture/network.md) - Network configuration
- [Backup and Recovery](../../../runbooks/backup-restore.md) - DR procedures

## Support

### Infrastructure Development
- **Repository**: [vm-platform](https://gitlab.com/stetter-homelab/vm-platform)
- **Documentation**: [VM Platform](../../vm-platform.md)
- **Issue Tracking**: GitLab Issues in vm-platform repository

### Development Environment
- **Devbox Documentation**: [devbox.sh](https://devbox.sh)
- **OpenTofu**: [opentofu.org](https://opentofu.org)
- **Ansible**: [docs.ansible.com](https://docs.ansible.com)

### Quick Reference

```bash
# SSH access patterns
ssh dev01                              # Direct access
ssh -A dev01                           # With agent forwarding
ssh -J dev01 ctr01                     # Jump through to ctr01

# Development environments
devbox shell                           # Enter project environment
devbox global list                     # List global tools
devbox search terraform               # Search for packages

# Infrastructure operations
tofu plan -out plan.out               # Plan changes
tofu apply plan.out                   # Apply planned changes
ansible-playbook site.yml -l host    # Run Ansible playbook

# Common directories
cd ~/projects/vm-platform            # Main IaC repository
cd ~/projects/vm-platform/terraform  # Infrastructure configs
cd ~/projects/vm-platform/ansible    # Automation playbooks
```