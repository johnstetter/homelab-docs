# Synology Stacks

Docker Compose stacks running on the Synology DS1621+ NAS (192.168.1.4).

**Repository:** [stetter-homelab/syn-stacks](https://gitlab.com/stetter-homelab/syn-stacks)

## Overview

The Synology NAS runs core infrastructure services that benefit from the stability and always-on nature of the NAS hardware. These services are intentionally kept separate from the primary Docker host (ctr01) to ensure critical infrastructure remains available even during container updates, host reboots, or maintenance on ctr01.

!!! info "Why Synology for Core Infrastructure?"
    The Synology runs primary DNS (Technitium) because:

    - **Stability** - Not subject to frequent container restarts during development
    - **Independence** - DNS remains available during ctr01 maintenance
    - **Always-on** - NAS is designed for 24/7 operation with minimal downtime
    - **Network foundation** - DNS is critical infrastructure that other services depend on

| Stack | Services | Purpose |
|-------|----------|---------|
| [technitium](#technitium) | Technitium DNS | Primary internal DNS |
| [pihole](#pihole) | Pi-hole | Ad blocking |
| [node-exporter](#node-exporter) | Node Exporter | Synology metrics |

## Synology Docker Environment

### Container Manager

Synology DSM 7.x uses Container Manager (Docker) for running containers. Stacks can be deployed via:

- **Container Manager UI** - Web-based management
- **SSH + Docker Compose** - Command-line deployment
- **Portainer** - Remote management from ctr01

### Storage Paths

| Path | Purpose |
|------|---------|
| `/volume1/docker` | Container data and configs |
| `/volume1/docker/stacks` | Docker Compose stacks |

### Resource Considerations

!!! warning "Limited Resources"
    The Synology has limited CPU compared to ctr01. Only run lightweight services here.

    - **CPU:** AMD Ryzen V1500B (4 cores)
    - **RAM:** 32GB (shared with DSM)

---

## Technitium

**Primary internal DNS server** for the entire homelab cluster.

!!! success "Primary DNS Node"
    This is the authoritative DNS server for the homelab. Running on the Synology ensures DNS remains stable and available independent of ctr01 container restarts, updates, or maintenance windows.

### Service Details

| Property | Value |
|----------|-------|
| **Image** | `technitium/dns-server:latest` |
| **Port** | 53 (DNS), 5380 (Web UI) |
| **IP** | 192.168.1.4 |
| **URL** | [dns.rsdn.io](https://dns.rsdn.io) |

### Features

- **Internal DNS Resolution** - All `*.rsdn.io` domains resolve internally
- **DNS-over-HTTPS** - Encrypted upstream queries
- **Query Logging** - All DNS queries logged for troubleshooting
- **Zone Management** - Internal zone for homelab services

### Configuration

```yaml
services:
  technitium:
    image: technitium/dns-server:latest
    container_name: technitium
    hostname: dns
    ports:
      - "53:53/udp"
      - "53:53/tcp"
      - "5380:5380/tcp"
    volumes:
      - ./config:/etc/dns
    environment:
      - DNS_SERVER_DOMAIN=dns.rsdn.io
      - DNS_SERVER_ADMIN_PASSWORD=${ADMIN_PASSWORD}
    restart: unless-stopped
```

### DNS Zones

**Primary Zone: rsdn.io**

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| traefik | A | 192.168.1.20 | Traefik dashboard |
| grafana | A | 192.168.1.20 | Grafana |
| plex | A | 192.168.1.20 | Plex Media Server |
| gitlab | A | 192.168.1.20 | GitLab |
| ha | A | 192.168.1.11 | Home Assistant |
| dns | A | 192.168.1.4 | This DNS server |
| *.rsdn.io | CNAME | traefik.rsdn.io | Wildcard for Traefik routing |

### Upstream DNS

Queries for external domains are forwarded to:

1. Pi-hole (192.168.1.4:5353) - Ad filtering
2. Cloudflare (1.1.1.1) - Fallback

### High Availability

The DNS cluster provides redundancy with zone transfer:

| Role | Host | IP | Notes |
|------|------|----|-------|
| **Primary** | syn (Synology) | 192.168.1.4 | Authoritative, stable |
| **Secondary** | ctr01 | 192.168.1.20 | Backup, syncs from primary |

**Why this architecture:**

- **Primary on Synology** - Isolated from ctr01 container churn; DNS stays up during ctr01 maintenance
- **Secondary on ctr01** - Provides redundancy if Synology is down for updates or hardware maintenance
- **Zone Transfer** - ctr01 Technitium syncs zones from Synology automatically

Clients should be configured with both DNS servers (primary first, then secondary).

---

## Pihole

Ad blocking DNS sinkhole.

### Service Details

| Property | Value |
|----------|-------|
| **Image** | `pihole/pihole:latest` |
| **Port** | 5353 (DNS), 8080 (Web UI) |
| **URL** | [pihole.rsdn.io](https://pihole.rsdn.io) |

### Features

- **Ad Blocking** - Blocks ads at DNS level
- **Tracking Protection** - Blocks known trackers
- **Statistics** - Query statistics and graphs
- **Custom Blocklists** - Additional blocklist sources

### Configuration

```yaml
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    ports:
      - "5353:53/tcp"
      - "5353:53/udp"
      - "8080:80/tcp"
    volumes:
      - ./etc-pihole:/etc/pihole
      - ./etc-dnsmasq.d:/etc/dnsmasq.d
    environment:
      - TZ=America/Chicago
      - WEBPASSWORD=${PIHOLE_PASSWORD}
      - PIHOLE_DNS_=1.1.1.1;8.8.8.8
    restart: unless-stopped
```

### Integration with Technitium

Technitium forwards queries to Pi-hole for ad filtering:

```
Client → Technitium (192.168.1.4:53) → Pi-hole (192.168.1.4:5353) → Cloudflare
```

### Blocklists

Default blocklists plus:

- Steven Black's Unified Hosts
- Energized Protection
- OISD blocklist

### Whitelisting

Common false positives are whitelisted:

- Microsoft services (some required for updates)
- Apple services
- Specific streaming services

---

## Node Exporter

Prometheus metrics exporter for Synology system metrics.

### Service Details

| Property | Value |
|----------|-------|
| **Image** | `prom/node-exporter:latest` |
| **Port** | 9100 |
| **Metrics** | [192.168.1.4:9100/metrics](http://192.168.1.4:9100/metrics) |

### Features

- **System Metrics** - CPU, memory, disk, network
- **Disk Health** - SMART metrics via text collector
- **Custom Metrics** - Synology-specific via text collector

### Configuration

```yaml
services:
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
      - ./textfile:/textfile:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.textfile.directory=/textfile'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
```

### Prometheus Integration

Prometheus on ctr01 scrapes this exporter:

```yaml
# prometheus.yml on ctr01
scrape_configs:
  - job_name: 'synology'
    static_configs:
      - targets: ['192.168.1.4:9100']
        labels:
          instance: 'syn'
```

### Grafana Dashboard

The "Node Exporter Full" dashboard in Grafana displays:

- CPU usage and load
- Memory usage
- Disk space and I/O
- Network throughput
- Temperature (if available)

---

## Deployment

### Via SSH

```bash
# SSH to Synology
ssh admin@192.168.1.4

# Navigate to stacks
cd /volume1/docker/stacks/stack-name

# Deploy
docker-compose up -d
```

### Via Container Manager

1. Open DSM web interface
2. Go to Container Manager > Project
3. Import docker-compose.yml
4. Configure environment variables
5. Start project

### Via Portainer

Portainer on ctr01 can manage Synology containers:

1. Add Synology as a Docker endpoint in Portainer
2. Deploy stacks through Portainer UI

---

## Backup

### Container Data

Container volumes are stored on `/volume1/docker` which is included in:

- **Hyper Backup** - Daily backup to external drive
- **Snapshot Replication** - Hourly snapshots

### Configuration Backup

Stack configurations are version-controlled in the [compose-stacks](https://gitlab.com/stetter-homelab/compose-stacks) group.

---

## Troubleshooting

### DNS Not Resolving

1. Check Technitium container is running:
   ```bash
   docker ps | grep technitium
   ```

2. Test DNS directly:
   ```bash
   dig @192.168.1.4 grafana.rsdn.io
   ```

3. Check Technitium logs:
   ```bash
   docker logs technitium
   ```

### Pi-hole Blocking Legitimate Sites

1. Access Pi-hole admin at [pihole.rsdn.io](https://pihole.rsdn.io)
2. Go to Query Log
3. Find blocked domain
4. Whitelist if needed

### Node Exporter Not Scraped

1. Verify exporter is running:
   ```bash
   curl http://192.168.1.4:9100/metrics
   ```

2. Check Prometheus targets:
   - Go to [prometheus.rsdn.io](https://prometheus.rsdn.io)
   - Check Status > Targets

---

## Related Documentation

- [ctr01 Stacks](ctr01.md)
- [Stack Overview](index.md)
- [Network Topology](../architecture/network.md)
- [Hardware Inventory](../architecture/hardware.md)
