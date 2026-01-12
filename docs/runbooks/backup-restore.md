# Backup and Restore

Complete guide to backup and recovery procedures for the Stetter Homelab.

## Overview

The homelab uses a multi-layered backup strategy to protect different types of data:

| Layer | Tool | Data Protected | Location |
|-------|------|----------------|----------|
| **Application data** | Backrest (restic) | Docker named volumes | Synology NFS |
| **NFS data** | Synology Hyper Backup | Bind mount data on NFS | Synology + offsite |
| **Configuration** | Git | Compose files, configs | GitLab |

## Prerequisites

- SSH access to ctr01
- Access to Synology DSM
- Access to [backrest.rsdn.io](https://backrest.rsdn.io)
- GitLab access to compose-stacks repositories

---

## Backup Infrastructure

### Synology Hyper Backup

Primary backup solution for all NFS-mounted data.

**What's protected:**

- `/volume1/docker/` - All stack data on NFS mounts
- `/volume1/media/` - Media files

**Schedule:**

- Daily incremental backups at 1:00 AM
- Full integrity check weekly

**Destinations:**

- Local USB drive (disaster recovery)
- Cloud backup (optional, for offsite)

### Backrest (Restic)

Backup solution for Docker named volumes not stored on NFS.

**What's protected:**

- Docker named volumes at `/var/lib/docker/volumes/`

**Schedule:**

- Daily at 2:00 AM
- Retention: 7 daily, 4 weekly, 3 monthly

**Repository location:** `/mnt/synology/docker/backups/restic-repo/`

For detailed Backrest operations, see [Backrest Service Documentation](../services/backrest.md).

### Git Version Control

All configuration is stored in Git for version control and disaster recovery.

**What's protected:**

- Docker Compose files
- Application configurations
- CI/CD pipelines
- Documentation

**Repositories:** [stetter-homelab/compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks)

---

## Per-Stack Backup Locations

| Stack | Data Location | Backup Method |
|-------|---------------|---------------|
| **core** | `/mnt/synology/docker/core/` | Hyper Backup |
| **monitoring** | `/mnt/synology/docker/monitoring/` | Hyper Backup |
| **management** | `/mnt/synology/docker/management/` | Hyper Backup |
| **automation** | `/mnt/synology/docker/automation/` | Hyper Backup |
| **media-servers** | `/mnt/synology/docker/media-servers/` | Hyper Backup |
| **media** | `/mnt/synology/docker/media/` | Hyper Backup |
| **ai** | `/mnt/synology/docker/ai/` | Hyper Backup |
| **frigate** | `/mnt/synology/docker/frigate/` | Hyper Backup |
| **dev-tools** | `/mnt/synology/docker/dev-tools/` | Hyper Backup |
| **gitlab** | `/mnt/synology/docker/gitlab/` | Hyper Backup |
| **technitium** | `/mnt/synology/docker/technitium/` | Hyper Backup |
| **mcp** | `/mnt/synology/docker/mcp/` | Hyper Backup |
| **Docker volumes** | `/var/lib/docker/volumes/` | Backrest |

---

## Docker Volume Backup Procedures

### Using Backrest for Scheduled Backups

Backrest automatically backs up Docker named volumes daily. To manually trigger a backup:

1. Go to [backrest.rsdn.io](https://backrest.rsdn.io)
2. Select the **docker-volumes** backup plan
3. Click **Run Now**
4. Monitor progress in the operations panel

### Manual Backup: Named Volumes

For one-off backups of Docker named volumes using tar:

```bash
# SSH to ctr01
ssh ctr01

# List all volumes
docker volume ls

# Backup a specific volume to NFS storage
docker run --rm \
  -v volume_name:/source:ro \
  -v /mnt/synology/docker/backups/manual:/backup \
  alpine tar czvf /backup/volume_name_$(date +%Y%m%d).tar.gz -C /source .

# Example: Backup portainer_data volume
docker run --rm \
  -v portainer_data:/source:ro \
  -v /mnt/synology/docker/backups/manual:/backup \
  alpine tar czvf /backup/portainer_data_$(date +%Y%m%d).tar.gz -C /source .
```

### Manual Backup: Bind Mounts on NFS

Data stored on NFS bind mounts (`/mnt/synology/docker/`) is automatically backed up by Synology Hyper Backup. For additional manual backups:

```bash
# SSH to ctr01
ssh ctr01

# Create a tarball of specific stack data
sudo tar czvf /mnt/synology/docker/backups/manual/grafana_$(date +%Y%m%d).tar.gz \
  -C /mnt/synology/docker/monitoring grafana

# Or use rsync for incremental backup
sudo rsync -av /mnt/synology/docker/monitoring/grafana/ \
  /mnt/synology/docker/backups/manual/grafana/
```

### Backup Verification

Verify backups are working correctly:

```bash
# Check Backrest backup status
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'

# Verify latest snapshot
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots --latest 1'

# Check backup integrity
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes check'

# Verify NFS storage is accessible
ssh ctr01 'ls -la /mnt/synology/docker/backups/'
```

---

## Docker Volume Restore Procedures

### Restore from Backrest/Restic Snapshots

For complete Backrest restore procedures, see [Backrest Service Documentation](../services/backrest.md#restore-procedures).

**Quick reference:**

1. **Stop the affected container:**
   ```bash
   ssh ctr01 'cd /opt/stacks/<stack> && docker compose stop <service>'
   ```

2. **List available snapshots:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'
   ```

3. **Restore to temporary location:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes restore <snapshot-id> \
     --target /tmp/restore \
     --include "/sources/docker-volumes/<volume-name>/_data"'
   ```

4. **Verify and copy to volume:**
   ```bash
   ssh ctr01 'ls -la /tmp/restore/sources/docker-volumes/<volume-name>/_data/'
   ssh ctr01 'sudo cp -a /tmp/restore/sources/docker-volumes/<volume-name>/_data/* \
     /var/lib/docker/volumes/<volume-name>/_data/'
   ```

5. **Restart container and clean up:**
   ```bash
   ssh ctr01 'cd /opt/stacks/<stack> && docker compose start <service>'
   ssh ctr01 'sudo rm -rf /tmp/restore'
   ```

### Restore from Manual Tar Backup

```bash
# SSH to ctr01
ssh ctr01

# Stop container using the volume
cd /opt/stacks/<stack>
docker compose stop <service>

# Clear volume contents (optional, if replacing all data)
docker run --rm -v volume_name:/data alpine rm -rf /data/*

# Restore from tarball
docker run --rm \
  -v volume_name:/data \
  -v /mnt/synology/docker/backups/manual:/backup:ro \
  alpine tar xzvf /backup/volume_name_YYYYMMDD.tar.gz -C /data

# Start container
docker compose start <service>
```

### Point-in-Time Recovery

For recovering data from a specific date/time:

```bash
# List snapshots with timestamps
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots --json' | jq '.[].time'

# Find snapshot ID for desired timestamp
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'

# Restore from specific snapshot
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes restore <snapshot-id> \
  --target /tmp/restore'
```

### Volume Recreation

If a volume needs to be completely recreated:

```bash
# Stop all containers using the volume
docker compose stop <service>

# Remove the volume (WARNING: data loss!)
docker volume rm volume_name

# Recreate volume
docker volume create volume_name

# Restore data from backup
docker run --rm \
  -v volume_name:/data \
  -v /mnt/synology/docker/backups/manual:/backup:ro \
  alpine tar xzvf /backup/volume_name_YYYYMMDD.tar.gz -C /data

# Start containers
docker compose start <service>
```

---

## Database-Specific Procedures

### PostgreSQL

**Backup:**

```bash
# Dump database to file
docker exec postgres pg_dump -U postgres dbname > /mnt/synology/docker/backups/postgres_dbname_$(date +%Y%m%d).sql

# Or dump all databases
docker exec postgres pg_dumpall -U postgres > /mnt/synology/docker/backups/postgres_all_$(date +%Y%m%d).sql

# Compressed backup
docker exec postgres pg_dump -U postgres dbname | gzip > /mnt/synology/docker/backups/postgres_dbname_$(date +%Y%m%d).sql.gz
```

**Restore:**

```bash
# Stop applications using the database
cd /opt/stacks/<stack>
docker compose stop <app-service>

# Drop and recreate database (if needed)
docker exec -it postgres psql -U postgres -c "DROP DATABASE IF EXISTS dbname;"
docker exec -it postgres psql -U postgres -c "CREATE DATABASE dbname;"

# Restore from dump
cat /mnt/synology/docker/backups/postgres_dbname_YYYYMMDD.sql | docker exec -i postgres psql -U postgres dbname

# Or from compressed backup
gunzip -c /mnt/synology/docker/backups/postgres_dbname_YYYYMMDD.sql.gz | docker exec -i postgres psql -U postgres dbname

# Start application
docker compose start <app-service>
```

### MariaDB / MySQL

**Backup:**

```bash
# Dump single database
docker exec mariadb mysqldump -u root -p$MYSQL_ROOT_PASSWORD dbname > /mnt/synology/docker/backups/mariadb_dbname_$(date +%Y%m%d).sql

# Dump all databases
docker exec mariadb mysqldump -u root -p$MYSQL_ROOT_PASSWORD --all-databases > /mnt/synology/docker/backups/mariadb_all_$(date +%Y%m%d).sql

# Compressed backup
docker exec mariadb mysqldump -u root -p$MYSQL_ROOT_PASSWORD dbname | gzip > /mnt/synology/docker/backups/mariadb_dbname_$(date +%Y%m%d).sql.gz
```

**Restore:**

```bash
# Stop applications using the database
docker compose stop <app-service>

# Restore from dump
cat /mnt/synology/docker/backups/mariadb_dbname_YYYYMMDD.sql | docker exec -i mariadb mysql -u root -p$MYSQL_ROOT_PASSWORD dbname

# Or from compressed backup
gunzip -c /mnt/synology/docker/backups/mariadb_dbname_YYYYMMDD.sql.gz | docker exec -i mariadb mysql -u root -p$MYSQL_ROOT_PASSWORD dbname

# Start application
docker compose start <app-service>
```

### SQLite

SQLite databases are file-based and must be backed up with the container stopped.

**Backup:**

```bash
# Stop container first to ensure consistency
docker compose stop <service>

# Copy database file
cp /mnt/synology/docker/<stack>/app.db /mnt/synology/docker/backups/app_db_$(date +%Y%m%d).db

# Or for named volumes
docker run --rm \
  -v volume_name:/source:ro \
  -v /mnt/synology/docker/backups:/backup \
  alpine cp /source/app.db /backup/app_db_$(date +%Y%m%d).db

# Start container
docker compose start <service>
```

**Restore:**

```bash
# Stop container
docker compose stop <service>

# Restore database file
cp /mnt/synology/docker/backups/app_db_YYYYMMDD.db /mnt/synology/docker/<stack>/app.db

# Fix permissions if needed
chown 1000:1000 /mnt/synology/docker/<stack>/app.db

# Start container
docker compose start <service>
```

---

## Disaster Recovery

### Complete Stack Recovery

To recover a complete stack from scratch:

1. **Clone configuration from GitLab:**
   ```bash
   git clone git@gitlab.com:stetter-homelab/compose-stacks/<stack>.git /opt/stacks/<stack>
   ```

2. **Create .env file:**
   ```bash
   cp /opt/stacks/<stack>/.env.example /opt/stacks/<stack>/.env
   vim /opt/stacks/<stack>/.env  # Add secrets
   ```

3. **Create data directories:**
   ```bash
   sudo mkdir -p /mnt/synology/docker/<stack>
   ```

4. **Restore data from Hyper Backup:**
   - Open Synology DSM
   - Go to Hyper Backup
   - Select backup task
   - Click "Restore" and choose files

5. **Restore Docker volumes from Backrest:**
   ```bash
   docker exec backrest restic -r /repos/docker-volumes restore latest \
     --target /tmp/restore \
     --include "/sources/docker-volumes/<volume-name>"
   ```

6. **Start the stack:**
   ```bash
   cd /opt/stacks/<stack>
   docker compose up -d
   ```

### Full Host Recovery

If ctr01 needs to be rebuilt completely:

1. **Rebuild VM using OpenTofu:**
   ```bash
   cd ~/projects/vm-platform/terraform/vms/ctr01
   tofu apply
   ```

2. **Run Ansible provisioning:**
   ```bash
   cd ~/projects/vm-platform/ansible
   ansible-playbook site.yml -l ctr01
   ```

3. **Mount NFS storage:**
   NFS mounts are configured by Ansible. Verify:
   ```bash
   ssh ctr01 'df -h | grep synology'
   ```

4. **Clone all stack repositories:**
   ```bash
   for stack in core monitoring management automation media-servers media ai frigate dev-tools gitlab technitium mcp; do
     git clone git@gitlab.com:stetter-homelab/compose-stacks/$stack.git /opt/stacks/$stack
   done
   ```

5. **Create .env files for each stack**

6. **Restore Docker volumes from Backrest:**
   ```bash
   docker exec backrest restic -r /repos/docker-volumes restore latest \
     --target /tmp/restore
   ```

7. **Start stacks in order:**
   ```bash
   cd /opt/stacks/core && docker compose up -d
   cd /opt/stacks/monitoring && docker compose up -d
   cd /opt/stacks/management && docker compose up -d
   # Continue for other stacks...
   ```

---

## Verification Checklist

### Daily Verification (Automated)

- [ ] Backrest daily backup completed
- [ ] No backup errors in Backrest UI
- [ ] Synology Hyper Backup task completed

### Weekly Verification

- [ ] Check Backrest backup status at [backrest.rsdn.io](https://backrest.rsdn.io)
- [ ] Verify backup integrity:
  ```bash
  ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes check'
  ```
- [ ] Check Hyper Backup status in Synology DSM
- [ ] Review backup storage space:
  ```bash
  ssh ctr01 'df -h /mnt/synology/docker/backups/'
  ```

### Monthly Verification

- [ ] Perform test restore of non-critical service
- [ ] Verify database dumps are valid:
  ```bash
  # Test PostgreSQL dump
  cat backup.sql | head -100
  ```
- [ ] Check snapshot retention policy is working:
  ```bash
  ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'
  ```
- [ ] Verify Git repositories are up to date with deployed configs

### Test Restore Procedure

Quarterly, perform a test restore to verify backups are actually recoverable:

1. **Choose a non-critical service** (e.g., IT-Tools, Flame)

2. **Stop the service:**
   ```bash
   ssh ctr01 'cd /opt/stacks/dev-tools && docker compose stop it-tools'
   ```

3. **Rename current data:**
   ```bash
   ssh ctr01 'mv /mnt/synology/docker/dev-tools/it-tools /mnt/synology/docker/dev-tools/it-tools.bak'
   ```

4. **Restore from backup:**
   Follow restore procedures above

5. **Verify service works:**
   ```bash
   curl -I https://tools.rsdn.io
   ```

6. **Clean up:**
   ```bash
   ssh ctr01 'rm -rf /mnt/synology/docker/dev-tools/it-tools.bak'
   ```

---

## Troubleshooting

### Backup Failed

1. **Check Backrest logs:**
   ```bash
   ssh ctr01 'docker logs backrest --tail 100'
   ```

2. **Check NFS mount:**
   ```bash
   ssh ctr01 'df -h | grep synology'
   ssh ctr01 'ls -la /mnt/synology/docker/backups/'
   ```

3. **Check disk space:**
   ```bash
   ssh ctr01 'df -h'
   ```

4. **Clear stale locks:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes unlock'
   ```

### Restore Failed

1. **Verify snapshot exists:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'
   ```

2. **Check permissions on destination:**
   ```bash
   ssh ctr01 'ls -la /var/lib/docker/volumes/<volume-name>/'
   ```

3. **Check available disk space:**
   ```bash
   ssh ctr01 'df -h /tmp'
   ```

4. **Try restoring a single file first:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes restore latest \
     --target /tmp/test \
     --include "/sources/docker-volumes/<volume>/testfile"'
   ```

### NFS Mount Issues

If NFS storage becomes unavailable:

1. **Check mount status:**
   ```bash
   ssh ctr01 'mount | grep synology'
   ssh ctr01 'df -h | grep synology'
   ```

2. **Check Synology NAS is accessible:**
   ```bash
   ping syn.rsdn.io
   ping 10.0.10.4  # Storage network
   ```

3. **Remount if needed:**
   ```bash
   ssh ctr01 'sudo umount /mnt/synology/docker'
   ssh ctr01 'sudo mount -a'
   ```

4. **Check NFS exports on Synology:**
   - Synology DSM > Control Panel > Shared Folder > NFS Permissions

---

## Related Documentation

- [Backrest Service Documentation](../services/backrest.md)
- [ctr01 Stacks](../stacks/ctr01.md)
- [Troubleshooting Runbook](troubleshooting.md)
- [Synology Stacks](../stacks/synology.md)
