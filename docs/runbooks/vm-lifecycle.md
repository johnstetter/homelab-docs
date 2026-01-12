# VM Lifecycle

Complete guide to creating, updating, and rebuilding VMs in the homelab.

## Overview

VMs are managed through the **vm-platform** repository using:

- **Packer**: Build golden images/templates
- **OpenTofu**: Provision and manage VM infrastructure
- **Ansible**: Configure VMs post-provisioning

**Repository:** [stetter-homelab/vm-platform](https://gitlab.com/stetter-homelab/vm-platform)

---

## Current VMs

| VM | Purpose | OS | Specs | IPs |
|----|---------|-----|-------|-----|
| ctr01 | Docker host | Debian 13 | 10 cores, 24GB RAM, RTX2000E ADA | 192.168.1.20 / 10.0.10.20 |
| dev01 | Development/bastion | Ubuntu 24.04 | 4 cores, 8GB RAM | 192.168.1.21 |

**Infrastructure:**

- **Hypervisor:** Proxmox 8.x on pve-ms-a2.rsdn.io (192.168.1.12)
- **Storage Network:** 10.0.10.0/24 (10G direct connection)
- **Management Network:** 192.168.1.0/24

---

## When to Rebuild vs Update

| Scenario | Action | Tool |
|----------|--------|------|
| Package updates | Update | Ansible |
| Configuration changes | Update | Ansible |
| New software installation | Update | Ansible |
| Major OS upgrade (e.g., Debian 12 to 13) | Rebuild | OpenTofu + Ansible |
| Corrupted system files | Rebuild | OpenTofu + Ansible |
| Starting fresh | Rebuild | OpenTofu + Ansible |
| Disk resize (grow) | Update | OpenTofu |
| CPU/RAM changes | Update | OpenTofu |

!!! tip "Prefer Updates"
    Always prefer Ansible updates over rebuilds when possible. Rebuilds require data backup/restore and service downtime.

---

## Creating a New VM

### Prerequisites

- SSH access to dev01
- Proxmox API credentials
- Devbox installed with vm-platform tools

### Step 1: Create Packer Template (if new OS)

If using a new OS version, create a Packer template first.

```bash
ssh dev01
cd ~/projects/vm-platform
devbox shell

# Create template directory
mkdir -p packer/ubuntu-24.04-docker-host
cd packer/ubuntu-24.04-docker-host
```

Create the Packer configuration based on existing templates in `packer/debian-docker-host/`.

```bash
# Build the template
packer init .
packer build -var-file=credentials.pkrvars.hcl .
```

### Step 2: Write OpenTofu Configuration

```bash
cd ~/projects/vm-platform/terraform/vms
mkdir -p new-vm
cd new-vm
```

Create `main.tf`:

```hcl
module "new_vm" {
  source = "../../modules/proxmox-vm"

  vm_name     = "new-vm"
  target_node = "nexus"
  vmid        = 101

  cores  = 4
  memory = 8192
  disk_size = "50G"

  clone_template = "debian-13-docker-template"

  network_config = {
    eth0 = {
      bridge = "vmbr0"
      ip     = "192.168.1.22/24"
      gw     = "192.168.1.1"
    }
  }

  ssh_keys = var.ssh_public_keys
}
```

### Step 3: Write Ansible Configuration

Add the VM to inventory:

```yaml
# ansible/inventory/hosts.yml
all:
  children:
    container_hosts:
      hosts:
        ctr01:
          ansible_host: 192.168.1.20
    dev_hosts:
      hosts:
        dev01:
          ansible_host: 192.168.1.21
        new-vm:
          ansible_host: 192.168.1.22
```

Create or assign roles in `ansible/site.yml`:

```yaml
- name: Configure new VM
  hosts: new-vm
  become: true
  roles:
    - common
    - dev-env
```

### Step 4: Run Pipeline or Local Commands

=== "Via CI/CD (Recommended)"

    ```bash
    git checkout -b feature/add-new-vm
    git add .
    git commit -m "feat: Add new-vm configuration"
    git push -u origin feature/add-new-vm
    glab mr create --title "feat: Add new-vm" --description "Adds new VM configuration"
    ```

    Review the plan in the pipeline, then merge to trigger apply.

=== "Local Development"

    ```bash
    cd ~/projects/vm-platform
    devbox shell

    # Apply OpenTofu
    cd terraform/vms/new-vm
    tofu init
    tofu plan
    tofu apply

    # Run Ansible
    cd ~/projects/vm-platform
    ansible-playbook ansible/site.yml -l new-vm
    ```

---

## Updating an Existing VM

### Software and Configuration Updates

Use Ansible for all software and configuration changes.

```bash
ssh dev01
cd ~/projects/vm-platform
devbox shell

# Update specific host
ansible-playbook ansible/site.yml -l ctr01

# Update with specific tags
ansible-playbook ansible/site.yml -l ctr01 --tags docker

# Dry run
ansible-playbook ansible/site.yml -l ctr01 --check --diff
```

### Infrastructure Updates (CPU, RAM, Disk)

Use OpenTofu for VM resource changes.

```bash
cd ~/projects/vm-platform/terraform/vms/ctr01
devbox shell

# Edit main.tf to change resources
vim main.tf

# Plan changes
tofu plan

# Apply (may require VM restart)
tofu apply
```

!!! warning "VM Restart Required"
    CPU and RAM changes typically require a VM restart. Schedule maintenance accordingly.

### Verification

```bash
# Verify SSH access
ssh ctr01 'hostname && uptime'

# Verify services
ssh ctr01 'docker ps'

# Verify GPU (ctr01 only)
ssh ctr01 'nvidia-smi'
```

---

## Rebuilding a VM

### Step 1: Backup Local Data

```bash
# Identify what needs backup
ssh ctr01 'ls -la /opt/stacks/'

# Backup any local state (most data should be on NFS)
ssh ctr01 'sudo tar -czf /mnt/synology/backups/ctr01-local-$(date +%Y%m%d).tar.gz /opt/stacks/'

# Verify NFS data is intact
ssh ctr01 'ls -la /mnt/synology/docker/'
```

!!! note "NFS-First Architecture"
    All persistent data should live on NFS at `/mnt/synology/docker/`. Local state should be minimal.

### Step 2: Destroy via OpenTofu

```bash
ssh dev01
cd ~/projects/vm-platform/terraform/vms/ctr01
devbox shell

# Review what will be destroyed
tofu plan -destroy

# Destroy the VM
tofu destroy
```

### Step 3: Recreate via OpenTofu

```bash
# Recreate the VM
tofu apply
```

### Step 4: Run Ansible

```bash
cd ~/projects/vm-platform
ansible-playbook ansible/site.yml -l ctr01
```

### Step 5: Restore Data

```bash
# Re-clone stacks
ssh ctr01 'cd /opt/stacks && git clone git@gitlab.com:stetter-homelab/compose-stacks/core.git'
ssh ctr01 'cd /opt/stacks && git clone git@gitlab.com:stetter-homelab/compose-stacks/monitoring.git'
# ... repeat for other stacks

# Copy .env files (from backup or recreate)
ssh ctr01 'cp /mnt/synology/backups/env-files/core.env /opt/stacks/core/.env'

# Start services
ssh ctr01 'cd /opt/stacks/core && docker compose up -d'
```

### Step 6: Verify

```bash
# Check all containers
ssh ctr01 'docker ps'

# Check NFS mounts
ssh ctr01 'df -h /mnt/synology'

# Check GPU (ctr01 only)
ssh ctr01 'nvidia-smi'

# Test web services
curl -I https://traefik.rsdn.io
```

---

## GPU Passthrough (ctr01)

### Overview

ctr01 has an NVIDIA RTX2000E ADA 16GB passed through from Proxmox for AI/ML workloads.

### Prerequisites

GPU passthrough must be configured in Proxmox before VM creation:

1. Enable IOMMU in BIOS
2. Enable IOMMU in Proxmox kernel parameters
3. Configure VFIO for GPU PCI devices
4. Verify IOMMU groups

### OpenTofu Configuration

```hcl
# In terraform/vms/ctr01/main.tf
hostpci = [
  {
    device  = "hostpci0"
    id      = "0000:01:00"  # GPU PCI address
    pcie    = true
    rombar  = true
  }
]
```

### Ansible NVIDIA Driver Installation

Drivers are installed via the `nvidia-drivers` Ansible role:

```bash
ansible-playbook ansible/site.yml -l ctr01 --tags nvidia
```

### Verification

```bash
# Check GPU visibility
ssh ctr01 'lspci | grep -i nvidia'

# Check drivers
ssh ctr01 'nvidia-smi'

# Test in container
ssh ctr01 'docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi'
```

---

## Cloud-Init

VMs use cloud-init for initial configuration during first boot.

### What Cloud-Init Handles

- Initial user creation
- SSH key injection
- Network configuration (static IPs)
- Hostname setting
- Initial package updates

### OpenTofu Cloud-Init Variables

```hcl
ciuser     = "stetter"
cipassword = var.vm_password
sshkeys    = var.ssh_public_keys

ipconfig0 = "ip=192.168.1.20/24,gw=192.168.1.1"
ipconfig1 = "ip=10.0.10.20/24"

nameserver = "192.168.1.4"
```

### Troubleshooting Cloud-Init

```bash
# Access via Proxmox console
# Check cloud-init status
cloud-init status

# View logs
cat /var/log/cloud-init.log
cat /var/log/cloud-init-output.log

# Re-run cloud-init (careful!)
cloud-init clean
cloud-init init
```

---

## Development Workflow

### Standard Workflow

```bash
# Connect to dev01
ssh dev01

# Navigate to repo
cd ~/projects/vm-platform

# Enter devbox environment
devbox shell

# Make changes
vim terraform/vms/ctr01/main.tf
vim ansible/roles/nvidia-drivers/tasks/main.yml

# Test locally
tofu plan
ansible-playbook ansible/site.yml -l ctr01 --check

# Commit and push
git add .
git commit -m "feat: Update ctr01 resources"
git push
```

### Available Devbox Tools

```bash
# Infrastructure
tofu --version      # OpenTofu
packer --version    # Packer
ansible --version   # Ansible

# Utilities
lazygit             # Git TUI
```

---

## Troubleshooting

### VM Won't Start

**Symptoms:** VM stuck in "starting" or immediately stops.

**Diagnosis:**

```bash
# Check Proxmox task log
ssh pve-ms-a2 'cat /var/log/pve/tasks/active'

# Check VM console in Proxmox web UI

# Check for locked VM
ssh pve-ms-a2 'qm status 100'
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| VM locked | `qm unlock 100` |
| GPU passthrough failed | Check IOMMU groups, reset GPU |
| Disk corruption | Restore from backup |
| Resource contention | Check other VMs, reduce allocation |

### Ansible Fails

**Symptoms:** Ansible playbook errors or timeouts.

**Diagnosis:**

```bash
# Test SSH connectivity
ssh ctr01 'echo ok'

# Check inventory
ansible-inventory --list

# Run with verbose output
ansible-playbook ansible/site.yml -l ctr01 -vvv
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| SSH key not found | Check `~/.ssh/id_ed25519` |
| Wrong inventory hostname | Verify `ansible/inventory/hosts.yml` |
| Python missing on target | Ensure `python3` is installed |
| Become password needed | Add `--ask-become-pass` |

### GPU Not Detected

**Symptoms:** `nvidia-smi` fails or shows no devices.

**Diagnosis:**

```bash
# Check PCI devices
lspci | grep -i nvidia

# Check kernel modules
lsmod | grep nvidia

# Check dmesg for errors
dmesg | grep -i nvidia
dmesg | grep -i vfio
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Passthrough not configured | Check Proxmox hostpci settings |
| Driver not loaded | Reinstall via Ansible: `ansible-playbook site.yml -l ctr01 --tags nvidia` |
| IOMMU disabled | Enable in BIOS and kernel params |
| GPU in use by host | Blacklist nouveau, configure VFIO |

### OpenTofu State Issues

**Symptoms:** State drift, resources not matching.

**Diagnosis:**

```bash
# Compare state to reality
tofu plan

# List state
tofu state list

# Show specific resource
tofu state show module.ctr01.proxmox_vm_qemu.vm
```

**Solutions:**

```bash
# Refresh state from reality
tofu refresh

# Import existing resource
tofu import module.ctr01.proxmox_vm_qemu.vm nexus/qemu/100

# Remove from state (careful!)
tofu state rm module.ctr01.proxmox_vm_qemu.vm
```

---

## Related Documentation

- [Adding New Stacks](new-stack.md)
- [Troubleshooting](troubleshooting.md)
- [vm-platform Repository](https://gitlab.com/stetter-homelab/vm-platform)
- [compose-stacks Repository](https://gitlab.com/stetter-homelab/compose-stacks)
