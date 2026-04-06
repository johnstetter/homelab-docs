# Talos Linux Platform

Talos Linux is a modern, immutable, and secure Kubernetes operating system that provides a minimal attack surface and declarative configuration. The Stetter Homelab runs active Talos Linux clusters with two different management approaches.

## Overview

**Talos Linux Benefits**:
- **Immutable OS**: No SSH access, no package manager, only Kubernetes API
- **Secure by Default**: Minimal attack surface, all services containerized
- **API-Driven**: Complete lifecycle management via APIs
- **Declarative**: Machine configuration as YAML
- **Zero-Trust**: Every component cryptographically verified

## Active Talos Clusters

### Talos Development Cluster (VMs 126-131)

**Location**: core.rsdn.io  
**Status**: 🟢 **Active Development**

| Node | VM ID | IP Address | Role | Specs |
|------|-------|------------|------|-------|
| talos-cp-1 | 126 | 192.168.1.126 | Control Plane | 2 vCPUs, 4GB RAM |
| talos-cp-2 | 127 | 192.168.1.127 | Control Plane | 2 vCPUs, 4GB RAM |
| talos-cp-3 | 128 | 192.168.1.128 | Control Plane | 2 vCPUs, 4GB RAM |
| talos-w-1 | 129 | 192.168.1.129 | Worker | 2 vCPUs, 4GB RAM |
| talos-w-2 | 130 | 192.168.1.130 | Worker | 2 vCPUs, 4GB RAM |
| talos-w-3 | 131 | 192.168.1.131 | Worker | 2 vCPUs, 4GB RAM |

**Cluster Configuration**:
- **HA Control Plane**: 3-node etcd cluster with raft consensus
- **Pod Network**: 10.244.0.0/16 (Flannel CNI)
- **Service Network**: 10.96.0.0/12
- **Storage**: Synology NFS for persistent volumes

## Management Approaches

Two parallel approaches are being developed to evaluate different operational models:

### 1. CLI-Based Management (talos-platform)

**Repository**: [talos-platform](https://gitlab.com/stetter-homelab/talos-platform)

**Philosophy**: Direct CLI interaction for hands-on cluster operations

#### Features
- **talosctl**: Primary management CLI for cluster operations
- **kubectl**: Standard Kubernetes management
- **Manual Configuration**: Hand-crafted machine configurations
- **Script-Based Operations**: Shell scripts for common tasks

#### Cluster Lifecycle

**Initial Setup**:
```bash
# Generate machine configurations
talosctl gen config homelab-talos https://192.168.1.126:6443 \
  --config-patch-control-plane @patches/controlplane.yaml \
  --config-patch-worker @patches/worker.yaml

# Apply configurations to nodes
talosctl apply-config --insecure \
  --nodes 192.168.1.126,192.168.1.127,192.168.1.128 \
  --file controlplane.yaml

talosctl apply-config --insecure \
  --nodes 192.168.1.129,192.168.1.130,192.168.1.131 \
  --file worker.yaml

# Bootstrap etcd cluster
talosctl bootstrap --nodes 192.168.1.126
```

**Daily Operations**:
```bash
# Get cluster status
talosctl --nodes 192.168.1.126 get members
talosctl --nodes 192.168.1.126 health

# Retrieve kubeconfig
talosctl kubeconfig --nodes 192.168.1.126

# Upgrade cluster
talosctl upgrade --nodes 192.168.1.126 \
  --image ghcr.io/siderolabs/talos:v1.6.1
```

#### Directory Structure
```
talos-platform/
├── configs/
│   ├── controlplane.yaml      # Control plane machine config
│   ├── worker.yaml            # Worker machine config
│   └── patches/               # Configuration patches
│       ├── controlplane.yaml  # CP-specific patches
│       └── worker.yaml        # Worker-specific patches
├── scripts/
│   ├── bootstrap.sh           # Initial cluster setup
│   ├── apply-config.sh        # Apply configurations
│   ├── upgrade.sh             # Cluster upgrade
│   └── backup.sh              # Backup cluster state
├── manifests/
│   └── workloads/             # Kubernetes manifests
└── docs/
    ├── procedures.md          # Operational procedures
    └── troubleshooting.md     # Common issues
```

### 2. Infrastructure as Code (talos-terraform-poc)

**Repository**: [talos-terraform-poc](https://gitlab.com/stetter-homelab/talos-terraform-poc)

**Philosophy**: Fully automated, GitOps-driven cluster management

#### Features
- **Terraform Provider**: `siderolabs/talos` for declarative management
- **Git-Based Workflow**: All configuration changes via pull requests
- **Automated Testing**: Cluster validation and workload deployment tests
- **State Management**: Terraform state tracks cluster configuration
- **CI/CD Integration**: Automated deployment pipeline

#### Terraform Resources

**Core Configuration**:
```hcl
# Talos machine secrets
resource "talos_machine_secrets" "cluster" {}

# Machine configurations
data "talos_machine_configuration" "controlplane" {
  cluster_name       = "homelab-talos"
  machine_type       = "controlplane"
  cluster_endpoint   = "https://192.168.1.126:6443"
  machine_secrets    = talos_machine_secrets.cluster.machine_secrets
  kubernetes_version = "1.29.0"
  
  config_patches = [
    file("${path.module}/patches/controlplane.yaml")
  ]
}

# Apply configurations
resource "talos_machine_configuration_apply" "controlplane" {
  count                       = 3
  client_configuration        = talos_machine_secrets.cluster.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration
  node                        = "192.168.1.${126 + count.index}"
}

# Bootstrap cluster
resource "talos_machine_bootstrap" "bootstrap" {
  depends_on = [talos_machine_configuration_apply.controlplane]
  client_configuration = talos_machine_secrets.cluster.client_configuration
  node                 = "192.168.1.126"
}
```

#### CI/CD Pipeline

**GitLab CI Stages**:
```yaml
stages:
  - validate
  - plan
  - apply
  - test

terraform-validate:
  stage: validate
  script:
    - terraform fmt -check
    - terraform validate

terraform-plan:
  stage: plan
  script:
    - terraform plan -out=plan.tfplan
  artifacts:
    paths: [plan.tfplan]

terraform-apply:
  stage: apply
  script:
    - terraform apply plan.tfplan
  when: manual
  only: [main]

cluster-test:
  stage: test
  script:
    - kubectl get nodes
    - kubectl apply -f tests/workloads/
    - kubectl wait --for=condition=Ready pods --all
```

#### Directory Structure
```
talos-terraform-poc/
├── terraform/
│   ├── main.tf                # Main Terraform configuration
│   ├── talos.tf               # Talos-specific resources
│   ├── proxmox.tf             # VM provisioning (future)
│   ├── variables.tf           # Input variables
│   └── outputs.tf             # Output values
├── patches/
│   ├── controlplane.yaml     # Control plane patches
│   └── worker.yaml           # Worker node patches
├── tests/
│   ├── workloads/            # Test Kubernetes workloads
│   └── scripts/              # Validation scripts
├── docs/
│   └── architecture.md       # Technical documentation
└── .gitlab-ci.yml            # CI/CD pipeline
```

## Comparison Matrix

| Aspect | CLI Approach | Terraform Approach |
|--------|-------------|-------------------|
| **Learning Curve** | Steeper (talosctl + kubectl) | Gentler (familiar Terraform) |
| **Automation Level** | Manual with scripts | Fully automated |
| **Configuration Drift** | Possible | Prevented by state management |
| **GitOps Integration** | Manual Git workflow | Native CI/CD pipeline |
| **Cluster Updates** | Manual talosctl commands | Automated via Terraform |
| **State Management** | External documentation | Terraform state file |
| **Rollback Process** | Manual intervention | Terraform plan rollback |
| **Development Speed** | Faster iteration | Slower, more thorough |
| **Production Readiness** | Requires manual oversight | Built-in validation |
| **Troubleshooting** | Direct CLI access | State file inspection |

## Operational Procedures

### Daily Operations

**Check Cluster Health**:
```bash
# CLI Approach
talosctl --nodes 192.168.1.126 health --server=false

# Terraform Approach  
terraform state show talos_machine_bootstrap.bootstrap
kubectl get nodes --show-labels
```

**View Cluster Dashboard**:
```bash
# Talos-specific dashboard
talosctl --nodes 192.168.1.126 dashboard

# Standard Kubernetes dashboard
kubectl proxy --port=8001
# Visit: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### Maintenance Procedures

**Cluster Upgrades**:
```bash
# CLI: Rolling upgrade
for node in 192.168.1.{126..131}; do
  talosctl upgrade --nodes $node --image ghcr.io/siderolabs/talos:v1.6.1
  sleep 60
done

# Terraform: Update version and apply
# Edit terraform/variables.tf:
# variable "talos_version" { default = "v1.6.1" }
terraform plan
terraform apply
```

**Configuration Updates**:
```bash
# CLI: Apply new patches
talosctl apply-config --nodes 192.168.1.126 --file controlplane.yaml

# Terraform: Update patches and apply
# Edit patches/controlplane.yaml
git commit -m "Update cluster configuration"
git push
# CI/CD pipeline applies changes automatically
```

### Troubleshooting

**Common Issues**:

| Issue | CLI Solution | Terraform Solution |
|-------|-------------|-------------------|
| **Node not joining** | `talosctl bootstrap` | `terraform apply -replace` |
| **etcd corruption** | Manual etcd recovery | Destroy/recreate with state |
| **Config drift** | Compare with Git | `terraform plan` shows drift |
| **Network issues** | `talosctl get addresses` | Check Terraform networking |

**Log Access**:
```bash
# System logs
talosctl --nodes 192.168.1.126 logs controller-runtime

# Kubernetes logs
kubectl logs -n kube-system -l component=kube-apiserver

# Service logs
kubectl logs -n kube-system -l k8s-app=flannel
```

## Storage Integration

### Synology NFS Storage

**PersistentVolume Example**:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: talos-nfs-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.1.4
    path: /volume1/k8s/talos
  storageClassName: nfs-synology
```

**StorageClass Configuration**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-synology
provisioner: nfs.csi.k8s.io
parameters:
  server: 192.168.1.4
  share: /volume1/k8s
  mountOptions: "vers=4.1,hard,intr,rsize=8192,wsize=8192"
allowVolumeExpansion: true
```

## Monitoring and Observability

### Prometheus Integration

**ServiceMonitor for Talos metrics**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: talos-metrics
spec:
  selector:
    matchLabels:
      app: talos-node-exporter
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

**Key Metrics**:
- Node resource utilization
- etcd cluster health
- Control plane component status
- Pod scheduling and resource requests

### Log Aggregation

**Fluent Bit configuration**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
data:
  fluent-bit.conf: |
    [INPUT]
        Name tail
        Path /var/log/containers/*.log
        Parser cri
        Tag kube.*
    
    [OUTPUT]
        Name loki
        Match *
        Host loki.monitoring.svc.cluster.local
        Port 3100
        Labels cluster=talos-dev
```

## Security Considerations

### Network Policies

**Default deny-all policy**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### RBAC Configuration

**Limited cluster-admin access**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: talos-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: User
  name: admin@rsdn.io
```

### Secret Management

**Sealed Secrets integration**:
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: database-credentials
spec:
  encryptedData:
    username: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAM...
    password: AghT4Y8s9U2s7wK3g9YzX8V1N4P6H8A...
```

## Next Steps

### Immediate (Q2 2025)
- [ ] Complete Terraform provider POC testing
- [ ] Standardize on preferred approach (CLI vs Terraform)
- [ ] Implement cluster backup and restore procedures
- [ ] Add Talos-specific monitoring dashboards

### Medium Term (Q3 2025)
- [ ] Deploy production workloads on Talos
- [ ] Implement GitOps with ArgoCD or Flux
- [ ] Add automated cluster lifecycle management
- [ ] Performance testing and optimization

### Long Term (Q4 2025)
- [ ] Evaluate Talos vs traditional K8s trade-offs
- [ ] Consider dedicated Talos hardware
- [ ] Implement zero-downtime update procedures
- [ ] Document lessons learned and best practices

## Related Documentation

- [Kubernetes Platform Overview](k8s-platform.md)
- [Infrastructure Architecture](../architecture/index.md)
- [Hardware Specifications](../architecture/hardware.md)
- [VM Platform](vm-platform.md)

## External Resources

- [Talos Linux Documentation](https://www.talos.dev/)
- [Talos Terraform Provider](https://registry.terraform.io/providers/siderolabs/talos/)
- [Talos GitHub Repository](https://github.com/siderolabs/talos)
- [Kubernetes Documentation](https://kubernetes.io/docs/)