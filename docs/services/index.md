# Service Catalog

Every web service and where it lives, as of 2026-10-30. All URLs are internal (LAN or tailnet) unless marked **public**.

## Platform

| Service | URL | Host | Stack |
|---------|-----|------|-------|
| [Traefik](traefik.md) | [traefik.rsdn.io](https://traefik.rsdn.io) | ctr01 | core |
| [Vault](vault.md) | [vault.rsdn.io](https://vault.rsdn.io) | ctr01 | core |
| [Authentik](authentik.md) | [sso.rsdn.io](https://sso.rsdn.io) | ctr01 | authentik |
| [Technitium](technitium.md) (primary) | [technitium-syn.rsdn.io](https://technitium-syn.rsdn.io) | syn | NAS |
| [Technitium](technitium.md) (secondary) | [technitium-ctr.rsdn.io](https://technitium-ctr.rsdn.io) | ctr01 | technitium |
| Pi-hole (legacy) | [pihole.rsdn.io](https://pihole.rsdn.io) | syn | NAS |

## AI

| Service | URL | Host | Notes |
|---------|-----|------|-------|
| [Open WebUI](open-webui.md) | [chat.rsdn.io](https://chat.rsdn.io) | Studio | Native LaunchDaemon |
| [Hermes Agent](hermes.md) | [hermes.rsdn.io](https://hermes.rsdn.io) | Studio | Native LaunchDaemon |
| [Ollama](ollama.md) (Studio) | `studio.rsdn.io:11434` | Studio | Hermes + Open WebUI |
| [Ollama](ollama.md) (ctr01) | `ctr01.rsdn.io:11434` | ctr01 | Home Assistant voice |
| [SearXNG](searxng.md) | [search.rsdn.io](https://search.rsdn.io) | ctr01 | ai stack |

## Monitoring

| Service | URL | Host |
|---------|-----|------|
| [Grafana](grafana.md) | [grafana.rsdn.io](https://grafana.rsdn.io) | ctr01 |
| [Prometheus](prometheus.md) | [prometheus.rsdn.io](https://prometheus.rsdn.io) | ctr01 |
| Alertmanager | [alertmanager.rsdn.io](https://alertmanager.rsdn.io) | ctr01 |
| [Loki](loki.md) | `ctr01.rsdn.io:3100` (no UI) | ctr01 |
| Promtail | [promtail.rsdn.io](https://promtail.rsdn.io) | ctr01 |

## Management

| Service | URL | Host |
|---------|-----|------|
| [Portainer](portainer.md) | [portainer.rsdn.io](https://portainer.rsdn.io) | ctr01 |
| Dozzle | [dozzle.rsdn.io](https://dozzle.rsdn.io) | ctr01 |
| [Semaphore](semaphore.md) | [semaphore.rsdn.io](https://semaphore.rsdn.io) | ctr01 |
| Pulse | [pulse.rsdn.io](https://pulse.rsdn.io) | ctr01 |
| [Backrest](backrest.md) | [backrest.rsdn.io](https://backrest.rsdn.io) | ctr01 |
| Proxmox (nexus) | [pve-nexus.rsdn.io](https://pve-nexus.rsdn.io) | nexus |
| Proxmox (pve-tc1) | [pve-hass.rsdn.io](https://pve-hass.rsdn.io) | pve-tc1 |
| DSM | [synology.rsdn.io](https://synology.rsdn.io) | syn |
| UniFi | [unifi.rsdn.io](https://unifi.rsdn.io) | rtr |

## Media

| Service | URL | Host |
|---------|-----|------|
| [Plex](plex.md) | [plex.rsdn.io](https://plex.rsdn.io) | ctr01 |
| Jellyfin | [jf.rsdn.io](https://jf.rsdn.io) (**public**) | ctr01 |
| Emby | [emby.rsdn.io](https://emby.rsdn.io) | ctr01 |
| Tautulli | [tautulli.rsdn.io](https://tautulli.rsdn.io) | ctr01 |
| Silo | [silo.rsdn.io](https://silo.rsdn.io), [silo-jf.rsdn.io](https://silo-jf.rsdn.io) | ctr01 |
| Tracearr | [tracearr.rsdn.io](https://tracearr.rsdn.io) | ctr01 |
| Dispatcharr | [dispatcharr.rsdn.io](https://dispatcharr.rsdn.io) | ctr01 |
| Seerr | [requests.rsdn.io](https://requests.rsdn.io) (**public**) | ctr01 |
| [Sonarr](sonarr.md) | [sonarr.rsdn.io](https://sonarr.rsdn.io) | ctr01 |
| [Radarr](radarr.md) | [radarr.rsdn.io](https://radarr.rsdn.io) | ctr01 |
| Lidarr | [lidarr.rsdn.io](https://lidarr.rsdn.io) | ctr01 |
| Bazarr | [bazarr.rsdn.io](https://bazarr.rsdn.io) | ctr01 |
| Prowlarr | [prowlarr.rsdn.io](https://prowlarr.rsdn.io) | ctr01 |
| SABnzbd | [sabnzbd.rsdn.io](https://sabnzbd.rsdn.io) | ctr01 |
| NZBGet | [nzbget.rsdn.io](https://nzbget.rsdn.io) | ctr01 |
| Tdarr | [tdarr.rsdn.io](https://tdarr.rsdn.io) | ctr01 |
| Tunarr | [tunarr.rsdn.io](https://tunarr.rsdn.io) | ctr01 |
| ARM | [arm.rsdn.io](https://arm.rsdn.io) | ctr01 |

## Development

| Service | URL | Host |
|---------|-----|------|
| GitLab CE | [gitlab.rsdn.io](https://gitlab.rsdn.io) | GitLab VM on syn |
| code-server | [code.rsdn.io](https://code.rsdn.io) | ctr01 |
| IT-Tools | [it-tools.rsdn.io](https://it-tools.rsdn.io) | ctr01 |
| PrivateBin | [privatebin.rsdn.io](https://privatebin.rsdn.io) | ctr01 |
| [Flame](flame.md) | [flame.rsdn.io](https://flame.rsdn.io) | ctr01 |

## Home and Web

| Service | URL | Host |
|---------|-----|------|
| Home Assistant | [home.rsdn.io](https://home.rsdn.io) | pve-tc1 (192.168.1.3) |
| stetter.io | [stetter.io](https://stetter.io) (**public**, via Cloudflare) | ctr01 |
| [Frigate](frigate.md) | frigate.rsdn.io | ctr01, **disabled** |

## Retired

| Service | Was | Now |
|---------|-----|-----|
| Open WebUI container | ctr01 ai stack | Native on the Studio |
| n8n, Whishper, LibreTranslate, vLLM | ctr01 ai stack | Removed (2026) |
| GitLab container | ctr01 gitlab stack | GitLab VM on the Synology |
| Jaeger tracing | ctr01 | Removed |
| Jellyfin on the Studio | Studio LaunchDaemon (Oct 2026) | Back on ctr01 |
