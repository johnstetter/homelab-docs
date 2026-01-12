# VM Platform

The vm-platform repository manages virtual machine provisioning and configuration for the Stetter Homelab.

**Repository:** [stetter-homelab/vm-platform](https://gitlab.com/stetter-homelab/vm-platform)

## Overview

This repository contains:

- **Packer templates** for building VM images
- **OpenTofu configurations** for provisioning VMs on Proxmox
- **Ansible playbooks** for post-provisioning configuration

## Repository Structure

```
vm-platform/
├── packer/
│   ├── debian-13.pkr.hcl      # Debian 13 template
│   ├── ubuntu-24.04.pkr.hcl   # Ubuntu 24.04 template
│   └── scripts/               # Provisioning scripts
├── tofu/
│   ├── main.tf                # Main configuration
│   ├── variables.tf           # Variable definitions
│   ├── terraform.tfvars       # Variable values
│   └── modules/
│       └── proxmox-vm/        # VM module
├── ansible/
│   ├── site.yml               # Main playbook
│   ├── inventory/             # Inventory files
│   └── roles/
│       ├── common/            # Base configuration
│       ├── docker/            # Docker installation
│       └── monitoring/        # Node exporter, etc.
├── devbox.json                # Development environment
└── .gitlab-ci.yml             # CI/CD pipeline
```

## VMs Managed

| VM Name | Template | vCPUs | RAM | Disk | Purpose |
|---------|----------|-------|-----|------|---------|
| ctr01 | Debian 13 | 8 | 32GB | 100GB | Docker host |
| dev01 | Ubuntu 24.04 | 4 | 16GB | 50GB | Dev/bastion |

## Packer Templates

### Building Templates

```bash
cd vm-platform/packer

# Build Debian 13 template
devbox run packer build debian-13.pkr.hcl

# Build Ubuntu 24.04 template
devbox run packer build ubuntu-24.04.pkr.hcl
```

### Template Features

All templates include:

- [x] QEMU guest agent
- [x] Cloud-init support
- [x] SSH key authentication
- [x] Docker CE pre-installed
- [x] Node Exporter for monitoring
- [x] Automatic security updates

### Example Packer Configuration

```hcl
source "proxmox-iso" "debian-13" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  node                     = "pve-ms-a2"

  iso_file                 = "local:iso/debian-13-amd64-netinst.iso"

  vm_name                  = "debian-13-template"
  template_description     = "Debian 13 template with Docker"

  cores                    = 2
  memory                   = 2048

  disk {
    type         = "scsi"
    disk_size    = "20G"
    storage_pool = "local-lvm"
  }

  network_adapters {
    model  = "virtio"
    bridge = "vmbr0"
  }

  cloud_init              = true
  cloud_init_storage_pool = "local-lvm"
}
```

## OpenTofu Configuration

### Provisioning VMs

```bash
cd vm-platform/tofu

# Initialize
devbox run tofu init

# Plan changes
devbox run tofu plan

# Apply changes
devbox run tofu apply
```

### Example VM Configuration

```hcl
module "ctr01" {
  source = "./modules/proxmox-vm"

  name        = "ctr01"
  target_node = "pve-ms-a2"
  clone       = "debian-13-template"

  cores  = 8
  memory = 32768

  disk_size = "100G"

  network {
    bridge = "vmbr0"
    ip     = "192.168.1.20/24"
    gw     = "192.168.1.1"
  }

  # GPU passthrough for Plex/Frigate/Ollama
  hostpci {
    device = "0000:01:00.0"
  }

  ssh_keys = var.ssh_public_keys
}
```

### State Management

OpenTofu state is stored locally and backed up:

```bash
# State location
tofu/terraform.tfstate

# Backup before changes
cp terraform.tfstate terraform.tfstate.backup
```

## Ansible Configuration

### Running Playbooks

```bash
cd vm-platform/ansible

# Run full site playbook
devbox run ansible-playbook site.yml

# Run specific role
devbox run ansible-playbook site.yml --tags docker

# Limit to specific host
devbox run ansible-playbook site.yml --limit ctr01
```

### Inventory

```ini
[docker_hosts]
ctr01 ansible_host=192.168.1.20

[dev_hosts]
dev01 ansible_host=192.168.1.21

[all:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/homelab
```

### Roles

| Role | Purpose | Applied To |
|------|---------|------------|
| common | Base packages, users, SSH | All hosts |
| docker | Docker CE, compose plugin | ctr01 |
| monitoring | Node exporter, promtail | All hosts |
| gpu | NVIDIA drivers, container toolkit | ctr01 |

## CI/CD Pipeline

The GitLab CI pipeline:

1. **Validate** - Check Packer, Tofu, and Ansible syntax
2. **Plan** - Show infrastructure changes
3. **Apply** - Deploy changes (manual trigger)

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - apply

validate:packer:
  stage: validate
  script:
    - packer validate packer/

validate:tofu:
  stage: validate
  script:
    - cd tofu && tofu init && tofu validate

validate:ansible:
  stage: validate
  script:
    - ansible-lint ansible/

plan:
  stage: plan
  script:
    - cd tofu && tofu plan -out=plan.tfplan
  artifacts:
    paths:
      - tofu/plan.tfplan

apply:
  stage: apply
  script:
    - cd tofu && tofu apply plan.tfplan
  when: manual
  only:
    - main
```

## Common Operations

### Rebuilding a VM

```bash
# 1. Destroy the VM
devbox run tofu destroy -target=module.ctr01

# 2. Rebuild from template
devbox run tofu apply

# 3. Run Ansible configuration
devbox run ansible-playbook site.yml --limit ctr01
```

### Updating Templates

```bash
# 1. Build new template
devbox run packer build packer/debian-13.pkr.hcl

# 2. Update Tofu to use new template
# Edit tofu/terraform.tfvars

# 3. Recreate VMs (plan first!)
devbox run tofu plan
devbox run tofu apply
```

### Adding a New VM

1. Add VM configuration to `tofu/main.tf`
2. Add to Ansible inventory
3. Create/update role assignments in `site.yml`
4. Run `tofu apply` then `ansible-playbook`

## Troubleshooting

!!! warning "Packer Build Fails"
    - Check Proxmox API credentials
    - Verify ISO is uploaded to Proxmox
    - Check Proxmox storage permissions

!!! warning "Tofu Apply Fails"
    - Verify template exists
    - Check Proxmox resource availability
    - Review state file for conflicts

!!! warning "Ansible Connection Fails"
    - Verify SSH key is correct
    - Check VM is running and accessible
    - Verify cloud-init completed

## Related Documentation

- [Hardware Inventory](../architecture/hardware.md) - VM host specifications
- [Network Topology](../architecture/network.md) - Network configuration
- [Adding New Stacks](../runbooks/new-stack.md) - Post-VM application deployment
