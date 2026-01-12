# Plex

Media streaming server with GPU-accelerated transcoding.

## Access

| Property | Value |
|----------|-------|
| **URL** | [plex.rsdn.io](https://plex.rsdn.io) |
| **Direct** | [plex.rsdn.io:32400/web](https://plex.rsdn.io:32400/web) |
| **Stack** | [compose-stacks/media-servers](https://gitlab.com/stetter-homelab/compose-stacks/media-servers) |
| **Port** | 32400 |
| **Image** | `plexinc/pms-docker:latest` |
| **GPU** | NVIDIA RTX2000E ADA (NVENC/NVDEC) |

## Authentication

Plex uses Plex.tv accounts for authentication.

**Claim token:** Required for initial setup. Get from [plex.tv/claim](https://plex.tv/claim)

---

## Common Operations

### Access Plex

1. Go to [plex.rsdn.io](https://plex.rsdn.io)
2. Sign in with Plex account
3. Select your server

### Scan Library

1. Go to **Settings** → **Manage** → **Libraries**
2. Click library name
3. Click **Scan Library Files**

Or use the API:
```bash
# Trigger library scan (requires X-Plex-Token)
curl "http://localhost:32400/library/sections/1/refresh?X-Plex-Token=YOUR_TOKEN"
```

### Add a Library

1. Go to **Settings** → **Manage** → **Libraries**
2. Click **Add Library**
3. Select type (Movies, TV Shows, Music, etc.)
4. Add folder: `/media/movies`, `/media/tv`, etc.
5. Configure scanner and agent

### Check Transcoding Status

1. Click **Settings** → **Status** → **Now Playing**
2. Look for "Transcode" indicator
3. Green = direct play, Yellow/Red = transcoding

### View Server Dashboard

1. Click **Settings** → **Status** → **Dashboard**
2. View active streams, bandwidth, history

---

## Media Library Structure

```
/media/
├── movies/
│   └── Movie Name (Year)/
│       └── Movie Name (Year).mkv
├── tv/
│   └── Show Name/
│       └── Season 01/
│           └── Show Name - S01E01 - Episode Title.mkv
├── music/
│   └── Artist/
│       └── Album/
│           └── 01 - Track.flac
└── photos/
    └── Year/
        └── Event/
```

**Naming conventions:** Follow [Plex naming guidelines](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/)

---

## GPU Transcoding

### Hardware Acceleration

Plex uses the RTX2000E ADA for:
- **NVDEC** - Hardware video decoding
- **NVENC** - Hardware video encoding
- **HDR Tone Mapping** - Hardware HDR to SDR conversion

### Check GPU Usage

```bash
# During active transcode
ssh ctr01 'nvidia-smi'

# You should see plex process using GPU
```

### Force Hardware Transcoding

In Plex settings:
1. **Settings** → **Transcoder**
2. Enable **Use hardware acceleration when available**
3. Enable **Use hardware-accelerated video encoding**

---

## Remote Access

### Enable Remote Access

1. **Settings** → **Remote Access**
2. Click **Enable Remote Access**
3. Configure port (32400) and bandwidth

### Custom Server URL

For Traefik routing:
1. **Settings** → **Network**
2. Set **Custom server access URLs**: `https://plex.rsdn.io:443`

### Troubleshoot Remote Access

```bash
# Check if port is accessible
curl -I https://plex.rsdn.io:32400/web

# Check Plex logs
docker logs plex | grep -i "remote"
```

---

## Configuration

### Data Locations

| Path | Description |
|------|-------------|
| Docker volume: `plex_config` | Plex database and metadata |
| `/mnt/synology/media` | Media files (read-only mount) |
| `/tmp/plex-transcode` | Transcode temp files (local SSD) |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `PLEX_CLAIM` | Initial claim token from plex.tv/claim |
| `PLEX_UID` / `PLEX_GID` | User/group for file permissions |
| `TZ` | Timezone |

### Preferences

Advanced settings in `Preferences.xml`:
```bash
# View current preferences
docker exec plex cat /config/Library/Application\ Support/Plex\ Media\ Server/Preferences.xml
```

---

## Optimization

### Transcode Settings

1. **Settings** → **Transcoder**
2. **Transcoder quality:** Prefer higher speed
3. **Background transcoding:** Faster encoding for mobile sync

### Direct Play/Stream

To avoid transcoding:
- Use compatible formats (H.264/H.265 + AAC)
- Match client resolution to source
- Disable subtitles or use SRT (not PGS/ASS)

### Database Optimization

```bash
# Optimize Plex database (stop Plex first)
docker exec plex /usr/lib/plexmediaserver/Plex\ Media\ Server --optimize-database
```

---

## Troubleshooting

### Library Not Updating

1. Check file permissions: media should be readable by PUID/PGID
2. Verify NFS mount: `ls /mnt/synology/media`
3. Force scan via API or UI
4. Check Plex logs: `docker logs plex | grep -i "scan"`

### Playback Buffering

1. **Check bandwidth:** Dashboard shows current throughput
2. **Reduce quality:** Try lower resolution
3. **Enable Direct Play:** Avoid transcoding
4. **Check NFS performance:** Network storage bottleneck

### Transcoding Failures

```bash
# Check transcoder logs
docker exec plex tail -100 /config/Library/Application\ Support/Plex\ Media\ Server/Logs/Plex\ Transcoder.log

# Verify GPU access
docker exec plex nvidia-smi
```

### Can't Find Server

1. Check container is running: `docker ps | grep plex`
2. Verify claim token was used during initial setup
3. Check network connectivity
4. Reclaim server at plex.tv/claim

### Metadata Not Matching

1. Verify file naming follows Plex conventions
2. Use "Fix Match" on incorrectly matched items
3. Check internet connectivity for metadata agents
4. Try different metadata agent

---

## Backup

### What to Backup

| Priority | Data | Location |
|----------|------|----------|
| Critical | Preferences, database | `plex_config` volume |
| Important | Watch history, playlists | Part of database |
| Optional | Metadata cache | Can be regenerated |

### Backup Command

```bash
# Stop Plex for consistent backup
docker compose stop plex

# Backup config volume
docker run --rm -v plex_config:/data -v /backup:/backup \
  alpine tar czf /backup/plex-config-$(date +%Y%m%d).tar.gz /data

# Start Plex
docker compose start plex
```

---

## Related Services

| Service | Purpose |
|---------|---------|
| [Sonarr](https://sonarr.rsdn.io) | TV show automation |
| [Radarr](https://radarr.rsdn.io) | Movie automation |
| [Tautulli](https://tautulli.rsdn.io) | Plex statistics |
| [Jellyfin](https://jellyfin.rsdn.io) | Open-source alternative |

---

## Related

- [Media Servers Stack](../stacks/ctr01.md#media-servers)
- [Plex Support](https://support.plex.tv/)
- [Tautulli](https://tautulli.com/)
