# Infrastructure Overview

The Stetter Homelab infrastructure is managed as code using a combination of Packer, OpenTofu (Terraform), and Ansible. This approach ensures reproducibility and makes it easy to rebuild the environment when needed.

## Infrastructure as Code Philosophy

> "Make it easy to rebuild when things inevitably break"

All infrastructure configuration lives in version-controlled GitLab repositories. Nothing is configured manually that can be automated.

## Repository Structure

| Repository | Purpose | Tools | Status |
|------------|---------|-------|--------|
| [vm-platform](https://gitlab.com/stetter-homelab/vm-platform) | VM provisioning and configuration | Packer, OpenTofu, Ansible | ✅ Active |
| [k8s-platform](https://gitlab.com/stetter-homelab/k8s-platform) | Kubernetes cluster management | OpenTofu, Helm | ✅ Active |
| [talos-platform](https://gitlab.com/stetter-homelab/talos-platform) | Talos Linux cluster management | talosctl, kubectl | ✅ Active |
| [talos-terraform-poc](https://gitlab.com/stetter-homelab/talos-terraform-poc) | Talos Infrastructure as Code | Terraform, Talos provider | 🔄 Development |
| [compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) | Docker Compose stacks (one repo per stack) | Docker Compose | ✅ Active |

## Provisioning Workflow

```mermaid
graph LR
    subgraph "Image Building"
        Packer[Packer] --> Template[VM Template]
    end

    subgraph "Infrastructure"
        OpenTofu[OpenTofu] --> VM[VM Instance]
        Template --> OpenTofu
    end

    subgraph "Configuration"
        Ansible[Ansible] --> Configured[Configured VM]
        VM --> Ansible
    end

    subgraph "Applications"
        Docker[Docker Compose] --> Running[Running Services]
        Configured --> Docker
    end
```

## Tool Stack

### Packer

Creates reproducible VM templates for Proxmox:

- **Base Images:** Debian 13, Ubuntu 24.04
- **Preinstalled:** Docker, monitoring agents, SSH keys
- **Output:** Proxmox VM templates

```bash
# Build a new template
cd vm-platform
devbox run packer build debian-13.pkr.hcl
```

### OpenTofu

Provisions VMs from templates:

- **Provider:** Proxmox (via bpg/proxmox)
- **State:** Local or GitLab-managed
- **Resources:** VMs, cloud-init, networking

```bash
# Plan and apply infrastructure
cd vm-platform
devbox run tofu plan
devbox run tofu apply
```

### Ansible

Configures VMs after provisioning:

- **Inventory:** Dynamic from OpenTofu state
- **Roles:** Docker, monitoring, security hardening
- **Playbooks:** Site-wide configuration

```bash
# Run configuration
cd vm-platform
devbox run ansible-playbook site.yml
```

### Docker Compose

Manages stateful containerized applications:

- **Primary Location:** ctr01 (MS-A2)
- **Secondary Location:** syn (Synology Container Manager)
- **Organization:** Stacks by function (compose-stacks repositories)
- **Deployment:** GitLab CI/CD or manual
- **Use Case:** Databases, media services, core infrastructure

```bash
# Deploy a stack
cd ~/projects/compose-stacks/monitoring
docker-compose up -d
```

### Kubernetes

Manages stateless and experimental workloads:

- **Location:** core.rsdn.io (multiple clusters)
- **Distributions:** K3s, Talos Linux
- **Management:** kubectl, talosctl, Terraform
- **Use Case:** Development, testing, stateless applications

```bash
# Access production K8s cluster
ssh core.rsdn.io
kubectl get nodes

# Access Talos cluster
talosctl --nodes 192.168.1.126 get members
```

## Development Environment

All IaC tools are managed via [Devbox](https://www.jetify.com/devbox) for reproducible development environments:

```bash
# Enter project environment
cd ~/projects/vm-platform
devbox shell

# Tools are now available
packer version
tofu version
ansible --version
```

See `devbox.json` in each repository for the specific tool versions.

## GitLab CI/CD Integration

Each repository has GitLab CI/CD configured for:

1. **Validation** - Syntax checking, linting
2. **Planning** - Show what will change
3. **Deployment** - Apply changes (manual trigger)

Example pipeline stages:

```yaml
stages:
  - validate
  - plan
  - apply

validate:
  script:
    - tofu validate
    - ansible-lint

plan:
  script:
    - tofu plan -out=plan.tfplan
  artifacts:
    paths:
      - plan.tfplan

apply:
  script:
    - tofu apply plan.tfplan
  when: manual
  only:
    - main
```

## State Management

### OpenTofu State

- **Location:** Local filesystem or GitLab-managed backend
- **Backup:** Committed to repository (encrypted sensitive values)
- **Locking:** GitLab-managed backend provides locking

### Docker Volume Data

- **Location:** Synology NFS mounts
- **Backup:** Daily snapshots via Synology Hyper Backup
- **Restore:** Mount backup and copy data

## Secrets Management

### HashiCorp Vault

Vault runs on ctr01 and manages:

- Docker registry credentials
- API keys for external services
- Database passwords
- SSL certificates (backup)

### Environment Files

Sensitive configuration in `.env` files:

- Never committed to git
- `.env.example` templates provided
- Stored in Vault for backup

## Next Steps

- [VM Platform Details](vm-platform.md)
- [VM Overview and Specifications](vms/vm-overview.md)
- [sec01 Security Testing VM](vms/sec01/README.md)
- [Kubernetes Platform Details](k8s-platform.md)
- [Talos Linux Platform](talos-platform.md)
- [Adding New Stacks](../runbooks/new-stack.md)
