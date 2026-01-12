# Flame

Flame is the primary dashboard and start page for the homelab infrastructure. It provides a unified interface for accessing all self-hosted applications and bookmarks.

## Overview

| Property | Value |
|----------|-------|
| **URL** | [flame.rsdn.io](https://flame.rsdn.io) |
| **Host** | ctr01 |
| **Stack** | dev-tools |
| **Image** | `pawelmalak/flame:latest` |
| **Port** | 5005 |

## Features

### Applications

Flame automatically displays Docker containers as application tiles. Each application shows:

- Service name and icon
- Direct link to the service URL (*.rsdn.io)

Applications are pulled from Docker labels, making it easy to add new services to the dashboard without manual configuration.

### Bookmarks

Bookmarks are organized into categories for quick access:

| Category | Examples |
|----------|----------|
| **Infrastructure** | Proxmox hosts, Technitium DNS, Home Assistant, Synology, UniFi |
| **Media** | Plex, Emby, Jellyfin, Tautulli |
| **AI** | ChatGPT, Claude, Perplexity, Gemini, OpenRouter |
| **Cloud** | AWS, Azure, GCP, OCI |
| **Local AI** | Open WebUI, SearXNG, Stable Diffusion |
| **K8S Services** | Grafana, Jaeger, Prometheus |
| **Dev Tools** | GitHub, GitLab |
| **Hosting** | Namecheap, Siteground |

### Weather Widget

Displays current weather conditions in the header.

### Greeting

Dynamic greeting based on time of day (Good morning/afternoon/evening).

## Docker Integration

Flame reads Docker labels to auto-discover applications. To add a service to Flame, include these labels in your `docker-compose.yml`:

```yaml
services:
  myapp:
    labels:
      - "flame.type=application"
      - "flame.name=My App"
      - "flame.url=https://myapp.rsdn.io"
      - "flame.icon=icon-name"
```

## Configuration

Flame stores its configuration in a persistent volume:

- **Config Path**: `/mnt/docker/flame/data`
- **Bookmarks**: Managed via the Flame web UI
- **Applications**: Auto-discovered from Docker or manually added

## Access

Flame is accessible at [flame.rsdn.io](https://flame.rsdn.io) and serves as the default homepage for the homelab.

## Related Services

- [Traefik](traefik.md) - Reverse proxy providing the *.rsdn.io routing
- [Portainer](portainer.md) - Docker management (complements Flame's overview)
