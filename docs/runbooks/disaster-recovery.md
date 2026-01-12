# Disaster Recovery

Complete disaster recovery procedures for the Stetter Homelab. This runbook covers scenarios from single service failures to complete infrastructure rebuilds.

## Overview

**Recovery Time Objectives (RTO):**

| Scenario | Target RTO | Priority |
|----------|-----------|----------|
| Single service failure | 15 minutes | Low |
| Stack failure | 30 minutes | Medium |
| ctr01 VM failure | 2-4 hours | High |
| Complete infrastructure failure | 8-12 hours | Critical |

**Recovery Point Objectives (RPO):**

| Data Type | Backup Frequency | Max Data Loss |
|-----------|-----------------|---------------|
| Configuration | Git (continuous) | 0 (version controlled) |
| Container data | Hourly snapshots | 1 hour |
| Media files | Daily | 24 hours |
| Database backups | Hourly | 1 hour |

---

## Prerequisites

Before attempting any recovery, ensure you have access to:

### Required Access

| Resource | Location | Credentials |
|----------|----------|-------------|
| Synology NAS | syn.rsdn.io / 192.168.1.4 | 1Password: "Synology Admin" |
| Proxmox | pve-ms-a2.rsdn.io / 192.168.1.12 | 1Password: "Proxmox Root" |
| GitLab | gitlab.com/stetter-homelab | SSH key or personal access token |
| Cloudflare | cloudflare.com | 1Password: "Cloudflare" |
| 1Password | 1password.com | Master password |

### Physical Access (if required)

- Network access to 192.168.1.0/24 subnet
- Console access to Proxmox (for VM boot issues)
- Physical access to Synology (for hardware failures)

### Recovery Tools

Ensure these are available on your recovery workstation:

```bash
# Required tools
ssh        # Remote access
git        # Clone repositories
glab       # GitLab CLI (optional)

# Recommended
mosh       # Persistent SSH sessions
tmux       # Terminal multiplexer
```

---

## Recovery Priority Order

When recovering from major failures, restore services in this order:

### Tier 1: Core Infrastructure (First 30 minutes)

1. **DNS (Technitium on Synology)** - Without DNS, nothing else resolves
2. **Traefik (reverse proxy)** - Required for all web access
3. **Vault (secrets)** - Required for other services to access credentials

### Tier 2: Monitoring (Next 30 minutes)

4. **Prometheus** - Metrics collection
5. **Grafana** - Dashboards and alerting
6. **Loki** - Log aggregation

### Tier 3: Management (Next 30 minutes)

7. **Portainer** - Container management UI
8. **Dozzle** - Log viewer
9. **Watchtower** - Auto-updates

### Tier 4: Applications (Remaining time)

10. **Media servers** - Plex, Jellyfin
11. **AI services** - Ollama, Open-WebUI
12. **Media automation** - Sonarr, Radarr
13. **Development tools** - code-server, GitLab
14. **Other stacks** - As needed

---

## Scenario 1: Single Service/Stack Failure

**Symptoms:** One container or stack is down, everything else works.

**Estimated Recovery Time:** 15-30 minutes

### Step 1: Diagnose the Failure

```bash
# SSH to ctr01
ssh ctr01

# Check container status
docker ps -a | grep service-name

# Check container logs
docker logs service-name --tail 100

# Check stack status
cd /opt/stacks/stack-name
docker compose ps
docker compose logs --tail 100
```

### Step 2: Attempt Simple Recovery

```bash
# Restart the container
docker restart service-name

# Or restart the entire stack
cd /opt/stacks/stack-name
docker compose down
docker compose up -d
```

### Step 3: If Simple Restart Fails

```bash
# Check for resource issues
df -h                          # Disk space
free -h                        # Memory
docker system df               # Docker disk usage

# Check NFS mounts
mount | grep synology
ls /mnt/synology/docker        # Test NFS access

# Check for image issues
docker compose pull            # Re-pull images
docker compose up -d
```

### Step 4: Restore from Backup (if data corrupted)

```bash
# Stop the service
docker compose down

# Identify latest backup
ls -la /mnt/synology/backups/stack-name/

# Restore data
rsync -av /mnt/synology/backups/stack-name/latest/ /mnt/synology/docker/stack-name/

# Start the service
docker compose up -d

# Verify
docker compose logs -f
```

### Verification Checklist

- [ ] Container is running: `docker ps | grep service-name`
- [ ] Logs show no errors: `docker logs service-name --tail 50`
- [ ] Web UI accessible (if applicable)
- [ ] Health checks passing (check Traefik dashboard)

---

## Scenario 2: ctr01 VM Failure

**Symptoms:** Cannot SSH to ctr01, all Docker services down, Proxmox shows VM offline.

**Estimated Recovery Time:** 2-4 hours

### Step 1: Assess the Failure

Access Proxmox to determine failure type:

```bash
# From local machine or dev01
ssh root@pve-ms-a2.rsdn.io

# Or access web UI
# https://pve-ms-a2.rsdn.io:8006
```

**Identify failure type:**

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| VM shows "stopped" | Crash or manual stop | Try starting VM |
| VM stuck in "starting" | Boot failure | Check console, may need rebuild |
| VM running but no network | Network config issue | Check VM network via console |
| VM disk locked | Storage issue | Check storage, unlock disk |

### Step 2: Attempt VM Recovery

**Option A: VM can be started**

```bash
# Via Proxmox CLI
qm start 100

# Or via web UI: click Start button
```

**Option B: VM boots but services fail**

Access console via Proxmox web UI and troubleshoot:

```bash
# Check system logs
journalctl -xb

# Check Docker
systemctl status docker

# Check NFS mounts
systemctl status mnt-synology-docker.mount
mount -a
```

**Option C: VM cannot boot - Rebuild required**

Continue to Step 3.

### Step 3: Rebuild ctr01 from Scratch

#### 3.1: Provision New VM via OpenTofu

```bash
# On dev01 or local machine with vm-platform repo
cd ~/projects/vm-platform/terraform/vms/ctr01

# Initialize and apply
tofu init
tofu apply

# This creates a new ctr01 VM with:
# - Debian 13
# - 10 cores, 24GB RAM
# - Network interfaces configured
# - Base OS installed
```

#### 3.2: Run Ansible Playbooks

```bash
cd ~/projects/vm-platform/ansible

# Run full playbook
ansible-playbook site.yml -l ctr01

# This configures:
# - Docker and Docker Compose
# - NVIDIA drivers for GPU passthrough
# - NFS mounts to Synology
# - User accounts and SSH keys
# - Base system configuration
```

#### 3.3: Verify Base System

```bash
ssh ctr01

# Verify Docker
docker info

# Verify GPU
nvidia-smi

# Verify NFS mounts
df -h | grep synology
ls /mnt/synology/docker
```

#### 3.4: Clone Stack Repositories

```bash
ssh ctr01

# Create stacks directory
sudo mkdir -p /opt/stacks
sudo chown $USER:$USER /opt/stacks

# Clone all stacks
cd /opt/stacks

# Core infrastructure (required first)
git clone git@gitlab.com:stetter-homelab/compose-stacks/core.git

# Monitoring
git clone git@gitlab.com:stetter-homelab/compose-stacks/monitoring.git

# Management
git clone git@gitlab.com:stetter-homelab/compose-stacks/management.git

# Remaining stacks
git clone git@gitlab.com:stetter-homelab/compose-stacks/automation.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/media-servers.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/media.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/ai.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/frigate.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/dev-tools.git
git clone git@gitlab.com:stetter-homelab/compose-stacks/mcp.git
```

!!! note "GitLab SSH Rate Limiting"
    If you encounter SSH connection issues, GitLab may be rate limiting. Wait a few minutes between clone operations.

#### 3.5: Restore Environment Files

Each stack needs a `.env` file with secrets. These are NOT stored in Git.

**Option A: Restore from Vault**

```bash
# If Vault backup exists and is accessible
vault kv get -format=json secret/stacks/core > /tmp/core-secrets.json
# Extract and create .env files
```

**Option B: Restore from Synology backup**

```bash
# Check for backed up .env files
ls /mnt/synology/backups/env-files/

# Copy to stacks
cp /mnt/synology/backups/env-files/core.env /opt/stacks/core/.env
cp /mnt/synology/backups/env-files/monitoring.env /opt/stacks/monitoring/.env
# ... repeat for each stack
```

**Option C: Recreate from 1Password**

For each stack, check `.env.example` and populate from 1Password:

```bash
cd /opt/stacks/core
cp .env.example .env
vim .env
# Fill in values from 1Password vault
```

#### 3.6: Start Stacks in Priority Order

```bash
# Tier 1: Core Infrastructure
cd /opt/stacks/core
docker compose up -d
# Wait for Traefik to be healthy
sleep 30
curl -I https://traefik.rsdn.io

# Tier 2: Monitoring
cd /opt/stacks/monitoring
docker compose up -d

# Tier 3: Management
cd /opt/stacks/management
docker compose up -d

# Tier 4: Applications
for stack in automation media-servers media ai frigate dev-tools mcp; do
  cd /opt/stacks/$stack
  docker compose up -d
  sleep 10
done
```

#### 3.7: Verify All Services

```bash
# Check all containers running
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check Traefik dashboard for healthy backends
curl -s http://localhost:8080/api/http/routers | jq '.[].status'

# Test key services
curl -I https://traefik.rsdn.io
curl -I https://grafana.rsdn.io
curl -I https://portainer.rsdn.io
curl -I https://plex.rsdn.io
```

### Verification Checklist

- [ ] ctr01 VM running in Proxmox
- [ ] SSH access working
- [ ] Docker daemon running
- [ ] GPU accessible (`nvidia-smi`)
- [ ] NFS mounts active
- [ ] All stacks deployed
- [ ] Traefik routing traffic
- [ ] Monitoring collecting metrics
- [ ] No errors in container logs

---

## Scenario 3: Complete Infrastructure Failure

**Symptoms:** Multiple systems down, Proxmox offline, possibly hardware failure.

**Estimated Recovery Time:** 8-12 hours

### Step 1: Triage Hardware

| System | Check | If Failed |
|--------|-------|-----------|
| Synology NAS | Power LED, network | Physical inspection required |
| UDM Pro | Status LEDs | Physical inspection, may need reset |
| Proxmox Host | Power, POST | Hardware diagnosis required |

### Step 2: Restore Network

**Priority 1: Internet connectivity**

1. Verify UDM Pro is operational
2. Check upstream ISP connection
3. Verify switch connectivity

**Priority 2: Internal networking**

1. Verify VLAN configuration
2. Check 10G storage network (if using)

### Step 3: Restore Synology NAS

The Synology is the source of truth for:

- Primary DNS (Technitium)
- All persistent data
- Backup storage

**If Synology is down:**

1. Check power and network connections
2. Access DSM web UI: https://192.168.1.4:5001
3. Check storage pool health in Storage Manager
4. Start required containers in Container Manager:
   - Technitium DNS (priority 1)
   - Pi-hole (priority 2)
   - Node Exporter (priority 3)

**If Synology storage is corrupted:**

1. Access DSM and check Storage Manager for degraded arrays
2. If RAID is recoverable, let it rebuild
3. If data loss occurred, restore from Hyper Backup (see [Data Recovery](#data-recovery))

### Step 4: Restore Proxmox

**If Proxmox host won't boot:**

1. Check BIOS/UEFI for boot order
2. Boot from Proxmox installer USB if needed
3. Reinstall Proxmox (VMs are stored on local storage)

**After Proxmox is operational:**

1. Verify storage pools
2. Check VM configurations
3. Import VMs if needed

### Step 5: Restore VMs

Follow [Scenario 2: ctr01 VM Failure](#scenario-2-ctr01-vm-failure) for each VM:

1. ctr01 (Docker host) - Priority 1
2. dev01 (Bastion/Dev) - Priority 2

### Step 6: Verify Complete System

Run through all verification checklists from Scenarios 1 and 2.

---

## Data Recovery

### From Synology Hyper Backup

Synology backs up to external storage. To restore:

1. Access DSM: https://192.168.1.4:5001
2. Open Hyper Backup
3. Select backup task
4. Click "Restore"
5. Choose data to restore:
   - `/volume1/docker` - All container data
   - `/volume1/media` - Media files

**Restore specific files:**

```bash
# SSH to Synology
ssh admin@192.168.1.4

# Navigate to backup explorer
# Use Hyper Backup Explorer in DSM
# Or mount backup directly
```

### From Backrest Snapshots

Backrest provides versioned snapshots for rapid recovery:

1. Access Backrest UI: https://backrest.rsdn.io
2. Navigate to repository
3. Browse snapshots by date
4. Restore to original location or new path

**CLI restore:**

```bash
# List available snapshots
restic -r /path/to/repo snapshots

# Restore specific snapshot
restic -r /path/to/repo restore <snapshot-id> --target /restore/path
```

### Configuration Recovery from Git

All stack configurations are version controlled:

```bash
# Clone fresh copy
git clone git@gitlab.com:stetter-homelab/compose-stacks/core.git

# Or reset existing repo
cd /opt/stacks/core
git fetch origin
git reset --hard origin/main
```

---

## DNS Restoration

### Primary DNS (Synology)

Primary DNS runs on Synology and should survive ctr01 failures.

**If Technitium on Synology is down:**

```bash
# SSH to Synology
ssh admin@192.168.1.4

# Check container
docker ps | grep technitium

# Start if stopped
cd /volume1/docker/stacks/technitium
docker-compose up -d
```

**If Technitium data is corrupted:**

1. Stop Technitium
2. Restore from backup:
   ```bash
   cp -r /volume1/backups/technitium/config /volume1/docker/technitium/
   ```
3. Start Technitium

### Secondary DNS (ctr01)

The secondary DNS on ctr01 syncs from Synology via zone transfer.

**After ctr01 rebuild:**

1. Start Technitium stack on ctr01
2. Configure zone transfer from primary:
   - Primary: 192.168.1.4
   - Secondary: 192.168.1.20
3. Verify zone sync in Technitium UI

### DNS Client Fallback

If both DNS servers are down, clients should fall back to public DNS.

**Temporary workaround:**

```bash
# On affected client
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
```

---

## SSL Certificate Recovery

### Automatic Recovery (Preferred)

Traefik will automatically request new certificates from Let's Encrypt:

1. Start Traefik with valid Cloudflare credentials
2. Wait 2-5 minutes for certificate provisioning
3. Verify in Traefik dashboard

### Manual Recovery from Backup

If you have a backup of `acme.json`:

```bash
# Stop Traefik
cd /opt/stacks/core
docker compose stop traefik

# Restore acme.json
cp /mnt/synology/backups/core/acme.json /mnt/synology/docker/core/traefik/acme.json

# Fix permissions
chmod 600 /mnt/synology/docker/core/traefik/acme.json

# Start Traefik
docker compose start traefik
```

### Cloudflare Credentials

Ensure Cloudflare API token is valid in `/opt/stacks/core/.env`:

```bash
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_DNS_API_TOKEN=your-api-token
```

Retrieve from 1Password if needed.

---

## Post-Recovery Verification

Complete this checklist after any recovery:

### Core Infrastructure

- [ ] DNS resolving: `dig traefik.rsdn.io @192.168.1.4`
- [ ] Traefik dashboard accessible: https://traefik.rsdn.io
- [ ] SSL certificates valid: `curl -vI https://any-service.rsdn.io 2>&1 | grep "SSL certificate"`
- [ ] Vault unsealed and accessible: https://vault.rsdn.io

### Monitoring

- [ ] Prometheus targets UP: https://prometheus.rsdn.io/targets
- [ ] Grafana dashboards loading: https://grafana.rsdn.io
- [ ] Loki receiving logs: Check Grafana Explore with Loki source

### Container Health

```bash
# All containers running
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -v "Up"

# No restart loops
docker ps --format "{{.Names}}: {{.Status}}" | grep -E "Restarting|Exited"

# Check for OOM kills
dmesg | grep -i "out of memory"
```

### Storage

```bash
# NFS mounts healthy
df -h | grep synology

# Write test
touch /mnt/synology/docker/test-file && rm /mnt/synology/docker/test-file

# Disk space adequate
df -h /mnt/synology/docker
```

### Network

```bash
# External connectivity
ping -c 3 8.8.8.8

# Internal DNS
dig @192.168.1.4 traefik.rsdn.io

# 10G network (if applicable)
iperf3 -c 10.0.10.4 -t 10
```

### Applications

- [ ] Plex accessible and streaming: https://plex.rsdn.io
- [ ] Grafana dashboards loading data
- [ ] Portainer showing all containers
- [ ] Media automation services connected

---

## Escalation and Help

### If Recovery Fails

1. **Document the issue:**
   - Screenshot error messages
   - Save relevant logs
   - Note exact steps that failed

2. **Check external resources:**
   - Service-specific documentation
   - GitHub/GitLab issues for the affected project
   - Reddit: r/selfhosted, r/homelab

3. **Community help:**
   - Discord: selfhosted, homelab channels
   - Post detailed question with logs

### Emergency Contacts

| Resource | Purpose |
|----------|---------|
| Synology Support | Hardware failures, DSM issues |
| Proxmox Forums | Hypervisor issues |
| ISP Support | Internet connectivity |

### Data Loss Prevention

If you suspect data loss:

1. **STOP** - Don't make changes that could overwrite data
2. Document what data might be affected
3. Check all backup sources before attempting recovery
4. Consider professional data recovery for critical data

---

## Preventive Measures

### Regular Backups

Verify these are running:

| Backup | Schedule | Verify Method |
|--------|----------|---------------|
| Hyper Backup | Daily | DSM > Hyper Backup > Last run |
| Backrest | Hourly | Backrest UI > Last snapshot |
| Git push | On commit | `git log origin/main` |

### Health Monitoring

Ensure alerts are configured for:

- Disk space > 80%
- Container restart loops
- Service down > 5 minutes
- Backup failures

### Documentation Updates

After any incident:

1. Update this runbook if procedures changed
2. Document any new failure modes
3. Update recovery time estimates based on actual experience

---

## Related Documentation

- [Troubleshooting](troubleshooting.md) - Common issues and quick fixes
- [Adding New Stacks](new-stack.md) - Stack deployment procedures
- [ctr01 Stacks](../stacks/ctr01.md) - Stack inventory
- [Synology Stacks](../stacks/synology.md) - Synology services
- [Architecture Overview](../architecture/index.md) - System design
- [vm-platform Repository](https://gitlab.com/stetter-homelab/vm-platform) - Infrastructure as Code
