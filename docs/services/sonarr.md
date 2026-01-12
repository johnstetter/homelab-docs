# Sonarr

Sonarr is a TV show management and automation tool that monitors for new episodes, downloads them via Usenet (SABnzbd), and organizes them in your media library.

## Access

| Property | Value |
|----------|-------|
| **URL** | [sonarr.rsdn.io](https://sonarr.rsdn.io) |
| **Stack** | [compose-stacks/media](https://gitlab.com/stetter-homelab/compose-stacks/media) |
| **Port** | 8989 |
| **Image** | `linuxserver/sonarr:latest` |

## Authentication

Sonarr uses Forms authentication by default. Credentials are configured during initial setup.

**API Key location:** Settings > General > Security > API Key

---

## Common Operations

### Add a TV Series

1. Navigate to **Series > Add New**
2. Search for the show by name
3. Configure options:
   - **Root Folder**: Select your TV library path (`/tv`)
   - **Quality Profile**: Choose desired quality (e.g., HD-1080p)
   - **Season Folder**: Enable for organized structure
   - **Monitor**: Select which seasons to track
4. Click **Add Series**

### Search for Episodes

```bash
# Manual search via UI
# Series > Select Show > Season > Search icon (magnifying glass)

# Or trigger via API
curl -X POST "https://sonarr.rsdn.io/api/v3/command" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "SeriesSearch", "seriesId": 1}'
```

### Configure Quality Profiles

1. Go to **Settings > Profiles**
2. Select or create a quality profile
3. Drag qualities to set preference order
4. Set cutoff (Sonarr stops upgrading at this quality)
5. Save changes

**Recommended profiles:**

- **HD-1080p**: Good balance of quality and size
- **Ultra-HD**: For 4K content (requires more storage)
- **Any**: Downloads first available quality

### Mass Editor

Bulk modify series settings:

1. Go to **Series > Mass Editor**
2. Select multiple series using checkboxes
3. Apply changes (quality profile, monitored status, etc.)
4. Click **Save**

---

## Integration with SABnzbd

Sonarr uses SABnzbd as its download client for Usenet content.

### Configure Download Client

1. Go to **Settings > Download Clients**
2. Click **+** to add client
3. Select **SABnzbd**
4. Configure:
   - **Host**: `sabnzbd` (container name) or `localhost`
   - **Port**: `8080`
   - **API Key**: From SABnzbd > Config > General
   - **Category**: `tv` (creates dedicated category)
5. Test and Save

### Download Workflow

```
Sonarr finds release → Sends to SABnzbd → SABnzbd downloads →
SABnzbd notifies Sonarr → Sonarr imports and renames → Files in library
```

---

## Configuration

### Root Folders

Configure where TV shows are stored:

1. **Settings > Media Management > Root Folders**
2. Add path: `/tv` (maps to NFS storage)

**Data location:**

| Path | Location |
|------|----------|
| Config | `/mnt/synology/docker/media/sonarr/config` |
| TV Library | `/mnt/synology/media/tv` |

### Naming Convention

**Settings > Media Management > Episode Naming**

Recommended format:
```
{Series Title} - S{season:00}E{episode:00} - {Episode Title} {Quality Full}
```

Example output: `Breaking Bad - S01E01 - Pilot HDTV-720p.mkv`

### Indexers

Configure Usenet indexers:

1. **Settings > Indexers**
2. Click **+** to add indexer
3. Select your indexer type (e.g., Newznab)
4. Enter API URL and key from your indexer provider

---

## Troubleshooting

### Episodes Not Importing

**Symptoms:** Downloads complete but files stay in download folder

**Causes and solutions:**

1. **Permission issues**
   ```bash
   # Check permissions on ctr01
   ssh ctr01
   ls -la /mnt/synology/docker/media/sabnzbd/downloads/complete/tv/

   # Files should be readable by sonarr container (PUID/PGID)
   ```

2. **Path mapping mismatch**
   - Verify SABnzbd's download path matches Sonarr's remote path mapping
   - Settings > Download Clients > SABnzbd > Remote Path Mappings

3. **Quality not matching**
   - Check Activity > Queue for rejection reasons
   - File quality may not meet profile requirements

### Manual Import

Force import stuck downloads:

1. Go to **Wanted > Manual Import**
2. Navigate to download folder
3. Select files and map to correct series/episodes
4. Click **Import**

### Series Not Searching

```bash
# Check Sonarr logs
ssh ctr01 'docker logs sonarr --tail 100'

# Common issues:
# - Indexer not responding (check Settings > Indexers > Test)
# - Series not monitored (enable monitoring)
# - No episodes in monitored seasons
```

### Container Not Starting

```bash
# Check container status
ssh ctr01 'docker ps -a | grep sonarr'

# View logs
ssh ctr01 'docker logs sonarr'

# Restart container
ssh ctr01 'cd /opt/stacks/media && docker compose restart sonarr'
```

### Database Locked

If Sonarr shows database errors:

```bash
# Stop container
ssh ctr01 'cd /opt/stacks/media && docker compose stop sonarr'

# Check for lock files
ssh ctr01 'ls -la /mnt/synology/docker/media/sonarr/config/*.db*'

# Remove lock files if present
ssh ctr01 'rm /mnt/synology/docker/media/sonarr/config/*.db-shm /mnt/synology/docker/media/sonarr/config/*.db-wal 2>/dev/null'

# Start container
ssh ctr01 'cd /opt/stacks/media && docker compose start sonarr'
```

---

## Backup & Recovery

### Backup

Sonarr configuration is backed up via Synology Hyper Backup.

**Manual backup:**
```bash
# Backup config directory
ssh ctr01 'tar -czf /tmp/sonarr-backup.tar.gz -C /mnt/synology/docker/media/sonarr .'
scp ctr01:/tmp/sonarr-backup.tar.gz ./
```

### Recovery

1. Stop Sonarr: `docker compose stop sonarr`
2. Restore config to `/mnt/synology/docker/media/sonarr/config`
3. Start Sonarr: `docker compose start sonarr`

---

## Related

- [Radarr](radarr.md) - Movie automation (same workflow)
- [SABnzbd](sabnzbd.md) - Usenet download client
- [Media Stack](../stacks/ctr01.md#media)
- [Sonarr Wiki](https://wiki.servarr.com/sonarr)
