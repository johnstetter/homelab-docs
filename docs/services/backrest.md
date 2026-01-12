# Backrest

Web UI for managing restic backup repositories. Provides backup scheduling, browsing, and restore capabilities for Docker volumes.

## Access

| Property | Value |
|----------|-------|
| **URL** | [backrest.rsdn.io](https://backrest.rsdn.io) |
| **Stack** | [compose-stacks/management](https://gitlab.com/stetter-homelab/compose-stacks/management) |
| **Port** | 9898 |
| **Image** | `garethgeorge/backrest:v1.10.1` |

## Authentication

Backrest uses its own authentication system. Configure credentials on first access.

---

## Common Operations

### View Backup Status

1. Go to [backrest.rsdn.io](https://backrest.rsdn.io)
2. The dashboard shows:
   - All configured backup plans
   - Last backup status per plan
   - Next scheduled backup time
   - Repository health status

### Trigger Manual Backup

1. Navigate to the backup plan
2. Click the **Run Now** button (play icon)
3. Monitor progress in the operations panel
4. Verify completion status

### View Backup History

1. Click on a backup plan
2. View the list of snapshots with timestamps
3. Click a snapshot to see included files and metadata

### Browse Backup Contents

1. Select a backup plan
2. Click on a specific snapshot
3. Navigate the file tree to view backed-up contents
4. Verify expected files are present

---

## Repository Configuration

### Current Repository Setup

| Repository | Path | Purpose |
|------------|------|---------|
| **docker-volumes** | `/repos/docker-volumes` | Docker named volumes backup |

**Source data location:** `/sources/docker-volumes` (mapped from `/var/lib/docker/volumes`)

### Repository Structure

```
/mnt/synology/docker/backups/restic-repo/
├── config
├── data/
├── index/
├── keys/
├── locks/
└── snapshots/
```

### Add a New Repository

1. Go to **Settings** → **Repositories**
2. Click **Add Repository**
3. Configure:
   - **Name:** Descriptive repository name
   - **Path:** Local path or remote URI
   - **Password:** Repository encryption password
4. Click **Create** and wait for initialization

### Add a New Backup Plan

1. Go to **Plans**
2. Click **Add Plan**
3. Configure:
   - **Name:** Backup plan name
   - **Repository:** Select target repository
   - **Paths:** Source paths to back up
   - **Schedule:** Cron expression for timing
   - **Retention:** How long to keep backups
4. Save and optionally run immediately

---

## Backup Schedules

### Default Schedule

| Plan | Schedule | Retention |
|------|----------|-----------|
| Docker Volumes | Daily at 2:00 AM | 7 daily, 4 weekly, 3 monthly |

### Schedule Format

Backrest uses cron expressions:

| Expression | Meaning |
|------------|---------|
| `0 2 * * *` | Daily at 2:00 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 3 * * 0` | Weekly on Sunday at 3:00 AM |
| `0 4 1 * *` | Monthly on the 1st at 4:00 AM |

### Modify Schedule

1. Click on the backup plan
2. Click **Edit**
3. Update the cron expression
4. Save changes

---

## Restore Procedures

### Restore Files via Web UI

1. Go to [backrest.rsdn.io](https://backrest.rsdn.io)
2. Select the backup plan containing your data
3. Click on the snapshot to restore from
4. Navigate to the file or directory
5. Click **Restore** and choose destination
6. Confirm the restore operation

!!! warning "Container Data Restore"
    When restoring Docker volume data, stop the affected container first
    to prevent data corruption.

### Restore via CLI (Recommended for Large Restores)

For more control, use restic directly on ctr01:

```bash
# SSH to ctr01
ssh ctr01

# List available snapshots
docker exec backrest restic -r /repos/docker-volumes snapshots

# Restore specific files to a temporary location
docker exec backrest restic -r /repos/docker-volumes restore latest \
  --target /tmp/restore \
  --include "/sources/docker-volumes/my_volume_name/_data"

# Or restore everything from a specific snapshot
docker exec backrest restic -r /repos/docker-volumes restore abc123 \
  --target /tmp/restore
```

### Full Volume Restore Procedure

When you need to restore an entire Docker volume:

1. **Stop the container using the volume:**
   ```bash
   ssh ctr01 'cd /opt/stacks/<stack> && docker compose stop <service>'
   ```

2. **Identify the snapshot to restore:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'
   ```

3. **Restore to a temporary location first:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes restore <snapshot-id> \
     --target /tmp/restore \
     --include "/sources/docker-volumes/<volume-name>/_data"'
   ```

4. **Verify restored data:**
   ```bash
   ssh ctr01 'ls -la /tmp/restore/sources/docker-volumes/<volume-name>/_data/'
   ```

5. **Copy data to the actual volume:**
   ```bash
   ssh ctr01 'sudo cp -a /tmp/restore/sources/docker-volumes/<volume-name>/_data/* \
     /var/lib/docker/volumes/<volume-name>/_data/'
   ```

6. **Start the container:**
   ```bash
   ssh ctr01 'cd /opt/stacks/<stack> && docker compose start <service>'
   ```

7. **Clean up temporary files:**
   ```bash
   ssh ctr01 'sudo rm -rf /tmp/restore'
   ```

### Point-in-Time Restore

To restore from a specific date/time:

1. **List snapshots with timestamps:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots --json' | jq
   ```

2. **Find snapshot ID for desired timestamp**

3. **Restore using that specific snapshot:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes restore <snapshot-id> \
     --target /tmp/restore'
   ```

---

## Verification and Maintenance

### Verify Backup Integrity

1. In Backrest UI, click on a repository
2. Click **Check** to verify repository integrity
3. Review results for any errors

CLI verification:
```bash
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes check'
```

### Verify Specific Snapshot

```bash
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes check --read-data-subset=1/10'
```

### Prune Old Backups

Backrest handles pruning automatically based on retention policy. Manual prune:

1. Click on the repository
2. Click **Prune**
3. Confirm the operation

CLI:
```bash
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes forget --prune \
  --keep-daily 7 --keep-weekly 4 --keep-monthly 3'
```

### View Repository Statistics

```bash
ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes stats'
```

---

## Configuration

### Data Locations

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/management/backrest/data` | Backrest application data |
| `/mnt/synology/docker/management/backrest/config` | Backrest configuration (config.json) |
| `/mnt/synology/docker/management/backrest/cache` | Restic cache directory |
| `/mnt/synology/docker/backups/restic-repo` | Restic repository storage |

### Volume Mounts

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| `/data` | `.../backrest/data` | Application database |
| `/config` | `.../backrest/config` | Configuration files |
| `/cache` | `.../backrest/cache` | Restic cache (improves performance) |
| `/repos/docker-volumes` | `.../backups/restic-repo` | Backup repository |
| `/sources/docker-volumes` | `/var/lib/docker/volumes` | Source data (read-only) |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `BACKREST_DATA` | Application data path |
| `BACKREST_CONFIG` | Configuration file path |
| `XDG_CACHE_HOME` | Cache directory |
| `TZ` | Timezone |

---

## Troubleshooting

### Backup Failed

1. **Check Backrest logs:**
   ```bash
   ssh ctr01 'docker logs backrest --tail 100'
   ```

2. **Common causes:**
   - **Disk full:** Check NFS storage space
   - **Lock file stale:** Another backup running or previous backup crashed
   - **Network issue:** NFS mount unavailable

3. **Clear stale locks (if sure no backup is running):**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes unlock'
   ```

### Repository Locked

If backups fail with "repository is already locked":

1. **Verify no backup is actually running**
2. **Check for stale locks:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes list locks'
   ```
3. **Remove stale lock:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes unlock'
   ```

### Can't Access Web UI

1. **Check container status:**
   ```bash
   ssh ctr01 'docker ps | grep backrest'
   ```

2. **Check Traefik routing:**
   - Verify backrest appears in [traefik.rsdn.io](https://traefik.rsdn.io)

3. **Check container logs:**
   ```bash
   ssh ctr01 'docker logs backrest --tail 50'
   ```

### NFS Mount Unavailable

If backups fail due to storage issues:

1. **Check NFS mount:**
   ```bash
   ssh ctr01 'df -h | grep synology'
   ssh ctr01 'ls -la /mnt/synology/docker/backups/'
   ```

2. **Remount if needed:**
   ```bash
   ssh ctr01 'sudo mount -a'
   ```

### Restore Failed

1. **Check available space** on destination
2. **Verify snapshot exists:**
   ```bash
   ssh ctr01 'docker exec backrest restic -r /repos/docker-volumes snapshots'
   ```
3. **Check permissions** on restore destination
4. **Try restoring a single file first** to isolate the issue

### Slow Backup Performance

1. **Check cache directory** is mounted and working
2. **Verify network throughput** to NFS storage
3. **Consider excluding large, frequently-changing files**
4. **Check if previous backup is still running**

---

## Backup Strategy Overview

### What's Backed Up

| Data | Method | Location |
|------|--------|----------|
| Docker named volumes | Backrest/restic | Synology NFS |
| Container configurations | Git repositories | GitLab |
| NFS data (media, etc.) | Synology Hyper Backup | Synology + offsite |

### Recovery Priority

| Priority | Data | Recovery Method |
|----------|------|-----------------|
| 1 | Configuration (compose files) | Git clone from GitLab |
| 2 | Application databases | Backrest restore |
| 3 | Media files | Synology restore |

---

## Related

- [Management Stack](../stacks/ctr01.md#management)
- [Backup and Restore Runbook](../runbooks/backup-restore.md)
- [Backrest Documentation](https://garethgeorge.github.io/backrest/)
- [Restic Documentation](https://restic.readthedocs.io/)
