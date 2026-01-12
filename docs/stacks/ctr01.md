# ctr01 Stacks

All Docker Compose stacks running on ctr01 (192.168.1.20), the primary Docker host.

**Repository:** [stetter-homelab/compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) (e.g., `compose-stacks/core`, `compose-stacks/monitoring`)

## Stack Overview

| Stack | Services | Status |
|-------|----------|--------|
| [core](#core) | Traefik, Vault | Active |
| [monitoring](#monitoring) | Prometheus, Grafana, Loki, Jaeger | Active |
| [management](#management) | Portainer, Dozzle, Semaphore | Active |
| [automation](#automation) | Watchtower | Active |
| [media-servers](#media-servers) | Plex, Jellyfin, Emby, Tautulli | Active |
| [media](#media) | Sonarr, Radarr, Lidarr, Bazarr, SABnzbd | Active |
| [ai](#ai) | Ollama, Open-WebUI, n8n, Whisper | Active |
| [frigate](#frigate) | Frigate, MQTT | Active |
| [dev-tools](#dev-tools) | code-server, Flame, IT-Tools | Active |
| [gitlab](#gitlab) | GitLab CE | Active |
| [technitium](#technitium-ctr01) | Technitium DNS | Active (Secondary/Backup) |
| [mcp](#mcp) | MCP Servers | Active |

---

## Core

Essential infrastructure services that all other stacks depend on.

### Traefik

Reverse proxy and SSL termination for all services.

| Property | Value |
|----------|-------|
| **Image** | `traefik:v3.0` |
| **Ports** | 80, 443 |
| **Dashboard** | [traefik.rsdn.io](https://traefik.rsdn.io) |

**Features:**

- Let's Encrypt wildcard certificates via Cloudflare DNS
- Automatic HTTPS redirect
- Docker provider for auto-discovery
- Middleware for authentication, rate limiting

**Configuration:**

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.dnschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=cloudflare"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./acme.json:/acme.json
    environment:
      - CF_API_EMAIL=${CLOUDFLARE_EMAIL}
      - CF_API_KEY=${CLOUDFLARE_API_KEY}
```

### Vault

HashiCorp Vault for secrets management.

| Property | Value |
|----------|-------|
| **Image** | `hashicorp/vault:1.15` |
| **Port** | 8200 |
| **URL** | [vault.rsdn.io](https://vault.rsdn.io) |

**Use Cases:**

- API keys and credentials
- Docker registry secrets
- Database passwords
- Certificate backup

---

## Monitoring

Comprehensive observability stack.

### Prometheus

Metrics collection and alerting.

| Property | Value |
|----------|-------|
| **Image** | `prom/prometheus:latest` |
| **Port** | 9090 |
| **URL** | [prometheus.rsdn.io](https://prometheus.rsdn.io) |

**Scrape Targets:**

- Node Exporter (all hosts)
- cAdvisor (container metrics)
- Traefik metrics
- Application exporters

### Grafana

Dashboards and visualization.

| Property | Value |
|----------|-------|
| **Image** | `grafana/grafana:latest` |
| **Port** | 3000 |
| **URL** | [grafana.rsdn.io](https://grafana.rsdn.io) |

**Dashboards:**

- Docker Host Overview
- Traefik Metrics
- Node Exporter Full
- Loki Logs
- Per-service dashboards

### Loki

Log aggregation.

| Property | Value |
|----------|-------|
| **Image** | `grafana/loki:latest` |
| **Port** | 3100 |

**Log Sources:**

- Promtail on all hosts
- Docker container logs
- Application logs

### Jaeger

Distributed tracing.

| Property | Value |
|----------|-------|
| **Image** | `jaegertracing/all-in-one:latest` |
| **Port** | 16686 |
| **URL** | [jaeger.rsdn.io](https://jaeger.rsdn.io) |

---

## Management

Container and infrastructure management tools.

### Portainer

Docker management UI.

| Property | Value |
|----------|-------|
| **Image** | `portainer/portainer-ce:latest` |
| **Port** | 9443 |
| **URL** | [portainer.rsdn.io](https://portainer.rsdn.io) |

**Features:**

- Container management
- Stack deployment
- Volume management
- Image management

### Dozzle

Real-time log viewer.

| Property | Value |
|----------|-------|
| **Image** | `amir20/dozzle:latest` |
| **Port** | 8080 |
| **URL** | [dozzle.rsdn.io](https://dozzle.rsdn.io) |

### Semaphore

Ansible automation UI.

| Property | Value |
|----------|-------|
| **Image** | `semaphoreui/semaphore:latest` |
| **Port** | 3000 |
| **URL** | [semaphore.rsdn.io](https://semaphore.rsdn.io) |

---

## Automation

### Watchtower

Automatic container updates.

| Property | Value |
|----------|-------|
| **Image** | `containrrr/watchtower:latest` |
| **Schedule** | Daily at 4 AM |

**Configuration:**

```yaml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_SCHEDULE=0 0 4 * * *
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_LABEL_ENABLE=true
```

!!! warning "Excluded Services"
    Add `com.centurylinklabs.watchtower.enable=false` label to critical services like Traefik, GitLab, and databases.

---

## Media Servers

Media streaming and management.

### Plex

Primary media server with hardware transcoding.

| Property | Value |
|----------|-------|
| **Image** | `plexinc/pms-docker:latest` |
| **Port** | 32400 |
| **URL** | [plex.rsdn.io](https://plex.rsdn.io) |
| **GPU** | RTX 2000E ADA (hardware transcoding) |

**Libraries:**

- Movies
- TV Shows
- Music

### Jellyfin

Open-source media server alternative.

| Property | Value |
|----------|-------|
| **Image** | `jellyfin/jellyfin:latest` |
| **Port** | 8096 |
| **URL** | [jellyfin.rsdn.io](https://jellyfin.rsdn.io) |

### Emby

Additional media server.

| Property | Value |
|----------|-------|
| **Image** | `emby/embyserver:latest` |
| **Port** | 8096 |
| **URL** | [emby.rsdn.io](https://emby.rsdn.io) |

### Tautulli

Plex monitoring and statistics.

| Property | Value |
|----------|-------|
| **Image** | `tautulli/tautulli:latest` |
| **Port** | 8181 |
| **URL** | [tautulli.rsdn.io](https://tautulli.rsdn.io) |

---

## Media

Media automation stack (behind VPN).

!!! note "VPN Protection"
    All services in this stack route through a VPN container for privacy.

### Sonarr

TV show automation.

| Property | Value |
|----------|-------|
| **Image** | `linuxserver/sonarr:latest` |
| **Port** | 8989 |
| **URL** | [sonarr.rsdn.io](https://sonarr.rsdn.io) |

### Radarr

Movie automation.

| Property | Value |
|----------|-------|
| **Image** | `linuxserver/radarr:latest` |
| **Port** | 7878 |
| **URL** | [radarr.rsdn.io](https://radarr.rsdn.io) |

### Lidarr

Music automation.

| Property | Value |
|----------|-------|
| **Image** | `linuxserver/lidarr:latest` |
| **Port** | 8686 |
| **URL** | [lidarr.rsdn.io](https://lidarr.rsdn.io) |

### Bazarr

Subtitle automation.

| Property | Value |
|----------|-------|
| **Image** | `linuxserver/bazarr:latest` |
| **Port** | 6767 |
| **URL** | [bazarr.rsdn.io](https://bazarr.rsdn.io) |

### SABnzbd

Usenet downloader.

| Property | Value |
|----------|-------|
| **Image** | `linuxserver/sabnzbd:latest` |
| **Port** | 8080 |
| **URL** | [sabnzbd.rsdn.io](https://sabnzbd.rsdn.io) |

---

## AI

AI and machine learning workloads.

### Ollama

Local LLM server.

| Property | Value |
|----------|-------|
| **Image** | `ollama/ollama:latest` |
| **Port** | 11434 |
| **GPU** | RTX 2000E ADA |

**Models:**

- llama3
- codellama
- mistral

### Open-WebUI

ChatGPT-like interface for Ollama.

| Property | Value |
|----------|-------|
| **Image** | `ghcr.io/open-webui/open-webui:main` |
| **Port** | 8080 |
| **URL** | [chat.rsdn.io](https://chat.rsdn.io) |

### n8n

Workflow automation.

| Property | Value |
|----------|-------|
| **Image** | `n8nio/n8n:latest` |
| **Port** | 5678 |
| **URL** | [n8n.rsdn.io](https://n8n.rsdn.io) |

### Whisper

Speech-to-text transcription.

| Property | Value |
|----------|-------|
| **Image** | `onerahmet/openai-whisper-asr-webservice:latest` |
| **Port** | 9000 |
| **GPU** | RTX 2000E ADA |

---

## Frigate

Network video recorder with AI object detection.

### Frigate NVR

| Property | Value |
|----------|-------|
| **Image** | `ghcr.io/blakeblackshear/frigate:stable` |
| **Port** | 5000 |
| **URL** | [frigate.rsdn.io](https://frigate.rsdn.io) |
| **GPU** | RTX 2000E ADA (object detection) |

**Features:**

- 24/7 recording
- Object detection (person, vehicle, animal)
- Home Assistant integration
- Motion zones

### MQTT (Mosquitto)

MQTT broker for Frigate events.

| Property | Value |
|----------|-------|
| **Image** | `eclipse-mosquitto:latest` |
| **Port** | 1883 |

---

## Dev Tools

Development and utility tools.

### code-server

VS Code in the browser.

| Property | Value |
|----------|-------|
| **Image** | `codercom/code-server:latest` |
| **Port** | 8443 |
| **URL** | [code.rsdn.io](https://code.rsdn.io) |

### Flame

Application dashboard.

| Property | Value |
|----------|-------|
| **Image** | `pawelmalak/flame:latest` |
| **Port** | 5005 |
| **URL** | [flame.rsdn.io](https://flame.rsdn.io) |

### IT-Tools

Developer utilities.

| Property | Value |
|----------|-------|
| **Image** | `corentinth/it-tools:latest` |
| **Port** | 80 |
| **URL** | [tools.rsdn.io](https://tools.rsdn.io) |

---

## GitLab

Self-hosted GitLab CE instance.

| Property | Value |
|----------|-------|
| **Image** | `gitlab/gitlab-ce:latest` |
| **Ports** | 80, 443, 22 |
| **URL** | [gitlab.rsdn.io](https://gitlab.rsdn.io) |

**Features:**

- Git repository hosting
- CI/CD pipelines
- Container registry
- Issue tracking

!!! warning "Resource Intensive"
    GitLab requires significant resources. Allocate at least 4GB RAM.

---

## Technitium (ctr01)

**Secondary/backup DNS server** for redundancy.

| Property | Value |
|----------|-------|
| **Image** | `technitium/dns-server:latest` |
| **Port** | 5380 (web), 53 (DNS) |
| **URL** | [dns-ctr01.rsdn.io](https://dns-ctr01.rsdn.io) |

!!! info "Backup DNS Node"
    This Technitium instance is the **secondary DNS** in the cluster. It syncs zones from the primary DNS on the Synology NAS via zone transfer.

    **Why secondary on ctr01?**

    - Primary DNS runs on Synology for stability (not subject to ctr01 container churn)
    - This provides redundancy if Synology is down for maintenance
    - Clients should use: Primary (192.168.1.4), Secondary (192.168.1.20)

**Configuration:**

- Receives zone transfers from primary (192.168.1.4)
- Read-only zones (changes made on primary only)
- Automatic sync keeps zones current

---

## MCP

Model Context Protocol servers for AI agents.

| Property | Value |
|----------|-------|
| **Image** | Various MCP server images |
| **Purpose** | Tools for Claude and other AI agents |

**Available Servers:**

- Filesystem MCP
- Git MCP
- Web search MCP

---

## Common Operations

### Starting a Stack

```bash
cd /opt/stacks/stack-name
docker compose up -d
```

### Viewing Logs

```bash
# All services in stack
docker compose logs -f

# Specific service
docker compose logs -f service-name
```

### Updating a Stack

```bash
docker compose pull
docker compose up -d
docker image prune -f
```

### Stopping a Stack

```bash
docker compose down
```

### Restarting a Service

```bash
docker compose restart service-name
```

## Related Documentation

- [Synology Stacks](synology.md)
- [Stack Overview](index.md)
- [Service Catalog](../services/index.md)
- [Adding New Stacks](../runbooks/new-stack.md)
