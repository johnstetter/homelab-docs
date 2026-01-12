# Radarr

Radarr is a movie management and automation tool that monitors for movies, downloads them via Usenet (SABnzbd), and organizes them in your media library.

## Access

| Property | Value |
|----------|-------|
| **URL** | [radarr.rsdn.io](https://radarr.rsdn.io) |
| **Stack** | [compose-stacks/media](https://gitlab.com/stetter-homelab/compose-stacks/media) |
| **Port** | 7878 |
| **Image** | `linuxserver/radarr:latest` |

## Authentication

Radarr uses Forms authentication by default. Credentials are configured during initial setup.

**API Key location:** Settings > General > Security > API Key

---

## Common Operations

### Add a Movie

1. Navigate to **Movies > Add New**
2. Search for the movie by title
3. Configure options:
   - **Root Folder**: Select your movie library path (`/movies`)
   - **Quality Profile**: Choose desired quality (e.g., HD-1080p)
   - **Minimum Availability**: When to search (Announced, In Cinemas, Released)
   - **Monitor**: Enable to track for downloads
4. Click **Add Movie**

### Search for Movies

```bash
# Manual search via UI
# Movies > Select Movie > Search icon (magnifying glass)

# Or trigger via API
curl -X POST "https://radarr.rsdn.io/api/v3/command" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "MoviesSearch", "movieIds": [1]}'
```

### Configure Quality Profiles

1. Go to **Settings > Profiles**
2. Select or create a quality profile
3. Drag qualities to set preference order
4. Set cutoff (Radarr stops upgrading at this quality)
5. Save changes

**Recommended profiles:**

- **HD-1080p**: Good balance of quality and size
- **Ultra-HD**: For 4K content (requires more storage)
- **Any**: Downloads first available quality

### Import Existing Movies

Add movies already in your library:

1. Go to **Movies > Library Import**
2. Select root folder containing movies
3. Radarr will scan and match movies
4. Review matches and import

### Mass Editor

Bulk modify movie settings:

1. Go to **Movies > Mass Editor**
2. Select multiple movies using checkboxes
3. Apply changes (quality profile, monitored status, root folder)
4. Click **Save**

---

## Integration with SABnzbd

Radarr uses SABnzbd as its download client for Usenet content.

### Configure Download Client

1. Go to **Settings > Download Clients**
2. Click **+** to add client
3. Select **SABnzbd**
4. Configure:
   - **Host**: `sabnzbd` (container name) or `localhost`
   - **Port**: `8080`
   - **API Key**: From SABnzbd > Config > General
   - **Category**: `movies` (creates dedicated category)
5. Test and Save

### Download Workflow

```
Radarr finds release → Sends to SABnzbd → SABnzbd downloads →
SABnzbd notifies Radarr → Radarr imports and renames → File in library
```

---

## Configuration

### Root Folders

Configure where movies are stored:

1. **Settings > Media Management > Root Folders**
2. Add path: `/movies` (maps to NFS storage)

**Data location:**

| Path | Location |
|------|----------|
| Config | `/mnt/synology/docker/media/radarr/config` |
| Movie Library | `/mnt/synology/media/movies` |

### Naming Convention

**Settings > Media Management > Movie Naming**

Recommended format:
```
{Movie Title} ({Release Year}) {Quality Full}
```

Folder format:
```
{Movie Title} ({Release Year})
```

Example output: `The Matrix (1999)/The Matrix (1999) Bluray-1080p.mkv`

### Indexers

Configure Usenet indexers:

1. **Settings > Indexers**
2. Click **+** to add indexer
3. Select your indexer type (e.g., Newznab)
4. Enter API URL and key from your indexer provider

### Custom Formats

Fine-tune quality preferences:

1. **Settings > Custom Formats**
2. Create formats for specific preferences (e.g., prefer x265, avoid 3D)
3. Assign scores in quality profiles
4. Higher scores = more preferred

---

## Troubleshooting

### Movies Not Importing

**Symptoms:** Downloads complete but files stay in download folder

**Causes and solutions:**

1. **Permission issues**
   ```bash
   # Check permissions on ctr01
   ssh ctr01
   ls -la /mnt/synology/docker/media/sabnzbd/downloads/complete/movies/

   # Files should be readable by radarr container (PUID/PGID)
   ```

2. **Path mapping mismatch**
   - Verify SABnzbd's download path matches Radarr's remote path mapping
   - Settings > Download Clients > SABnzbd > Remote Path Mappings

3. **Quality not matching**
   - Check Activity > Queue for rejection reasons
   - File quality may not meet profile requirements

### Manual Import

Force import stuck downloads:

1. Go to **Wanted > Manual Import**
2. Navigate to download folder
3. Select files and map to correct movie
4. Click **Import**

### Movie Not Found

If Radarr can't find a movie:

1. Try searching by TMDB ID or IMDB ID
2. Check [The Movie Database](https://www.themoviedb.org/) for correct title
3. Movie may not be in TMDB yet (add it there first)

### Container Not Starting

```bash
# Check container status
ssh ctr01 'docker ps -a | grep radarr'

# View logs
ssh ctr01 'docker logs radarr'

# Restart container
ssh ctr01 'cd /opt/stacks/media && docker compose restart radarr'
```

### Database Locked

If Radarr shows database errors:

```bash
# Stop container
ssh ctr01 'cd /opt/stacks/media && docker compose stop radarr'

# Check for lock files
ssh ctr01 'ls -la /mnt/synology/docker/media/radarr/config/*.db*'

# Remove lock files if present
ssh ctr01 'rm /mnt/synology/docker/media/radarr/config/*.db-shm /mnt/synology/docker/media/radarr/config/*.db-wal 2>/dev/null'

# Start container
ssh ctr01 'cd /opt/stacks/media && docker compose start radarr'
```

### Disk Space Issues

```bash
# Check available space
ssh ctr01 'df -h /mnt/synology/media/movies'

# Find largest movies
ssh ctr01 'du -sh /mnt/synology/media/movies/* | sort -hr | head -20'
```

---

## Backup & Recovery

### Backup

Radarr configuration is backed up via Synology Hyper Backup.

**Manual backup:**
```bash
# Backup config directory
ssh ctr01 'tar -czf /tmp/radarr-backup.tar.gz -C /mnt/synology/docker/media/radarr .'
scp ctr01:/tmp/radarr-backup.tar.gz ./
```

### Recovery

1. Stop Radarr: `docker compose stop radarr`
2. Restore config to `/mnt/synology/docker/media/radarr/config`
3. Start Radarr: `docker compose start radarr`

---

## Related

- [Sonarr](sonarr.md) - TV show automation (same workflow)
- [SABnzbd](sabnzbd.md) - Usenet download client
- [Media Stack](../stacks/ctr01.md#media)
- [Radarr Wiki](https://wiki.servarr.com/radarr)
