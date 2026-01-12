# Loki

Log aggregation system for collecting and querying container and system logs.

## Access

| Property | Value |
|----------|-------|
| **URL** | Internal only (query via Grafana) |
| **Stack** | [compose-stacks/monitoring](https://gitlab.com/stetter-homelab/compose-stacks/monitoring) |
| **Port** | 3100 |
| **Image** | `grafana/loki:3.6.3` |

Loki is not exposed externally. Query logs through [Grafana Explore](https://grafana.rsdn.io/explore).

---

## Architecture

```
┌─────────────────┐     ┌─────────────┐     ┌──────────┐
│   Containers    │────►│  Promtail   │────►│   Loki   │
│   (Docker)      │     │  (shipper)  │     │ (store)  │
└─────────────────┘     └─────────────┘     └──────────┘
                                                  │
┌─────────────────┐     ┌─────────────┐           │
│  System Logs    │────►│  Promtail   │───────────┤
│  (/var/log)     │     │             │           │
└─────────────────┘     └─────────────┘           │
                                                  ▼
┌─────────────────┐     ┌─────────────┐     ┌──────────┐
│  Syslog/UDP     │────►│   Vector    │────►│  Grafana │
│  (network)      │     │             │     │  (query) │
└─────────────────┘     └─────────────┘     └──────────┘
```

**Components:**
- **Promtail** - Collects Docker container logs and system logs
- **Vector** - Receives syslog over UDP (port 5514)
- **Loki** - Stores and indexes logs
- **Grafana** - Query and visualize logs

---

## Common LogQL Queries

### Basic Log Selection

```logql
# All logs from a container
{container="traefik"}

# Logs from specific compose project
{compose_project="monitoring"}

# Logs from specific compose service
{compose_service="grafana"}

# All Docker container logs
{job="docker"}

# System logs
{job="varlogs"}

# Logs from specific host
{host="ctr01"}
```

### Text Filtering

```logql
# Contains text (case-sensitive)
{container="traefik"} |= "error"

# Does not contain text
{container="traefik"} != "health"

# Case-insensitive match
{container="traefik"} |~ "(?i)error"

# Regex match
{container="traefik"} |~ "status=[45][0-9][0-9]"

# Multiple filters (AND)
{container="traefik"} |= "error" != "health"

# Negative regex
{container="nginx"} !~ "GET /health"
```

### JSON Log Parsing

```logql
# Parse JSON and filter by field
{container="traefik"} | json | status >= 400

# Extract specific field
{container="traefik"} | json | line_format "{{.RequestPath}}"

# Filter by parsed JSON field
{container="traefik"} | json | msg=~".*timeout.*"

# Parse nested JSON
{container="ollama"} | json | line_format "{{.level}}: {{.msg}}"
```

### Label Extraction

```logql
# Extract labels from log line using regex
{container="nginx"} | regexp `(?P<method>\w+) (?P<path>\S+) (?P<status>\d+)`

# Use extracted label for filtering
{container="nginx"}
| regexp `status=(?P<status>\d+)`
| status >= 400

# Parse key=value pairs
{container="traefik"} | pattern `<_> <method> <path> <_> <status>`
```

### Aggregations and Metrics

```logql
# Count logs per container (last hour)
sum by(container) (count_over_time({job="docker"}[1h]))

# Error rate per service
sum by(compose_service) (rate({job="docker"} |= "error"[5m]))

# Top 10 containers by log volume
topk(10, sum by(container) (rate({job="docker"}[1h])))

# Bytes ingested per container
sum by(container) (bytes_over_time({job="docker"}[1h]))
```

---

## Common Use Cases

### Find Errors in All Containers

```logql
{job="docker"} |~ "(?i)(error|exception|fatal|panic)"
```

### Traefik Access Logs

```logql
# All requests
{container="traefik"} | json

# 5xx errors
{container="traefik"} | json | OriginStatus >= 500

# Slow requests (>1s)
{container="traefik"} | json | Duration > 1000000000

# Requests to specific service
{container="traefik"} | json | ServiceName=~".*grafana.*"

# Failed SSL handshakes
{container="traefik"} |= "TLS handshake error"
```

### Container Startup/Shutdown

```logql
# Container start messages
{container="traefik"} |~ "(starting|started|listening|ready)"

# Container errors on startup
{container="ollama"} |= "error" | line_format "{{.msg}}"
```

### Debug Specific Container

```logql
# Last 100 lines from container
{container="frigate"} | tail 100

# With timestamp
{container="frigate"} | line_format "{{.ts}} {{.msg}}"

# Specific time range (use Grafana time picker)
{container="frigate"} |= "detection"
```

### System Logs

```logql
# SSH auth failures
{job="varlogs"} |~ "sshd.*Failed"

# Kernel errors
{job="varlogs"} |~ "kernel.*error"

# Docker daemon logs
{job="varlogs"} |= "dockerd"
```

---

## Log Labels

Promtail automatically adds these labels to Docker container logs:

| Label | Description | Example |
|-------|-------------|---------|
| `job` | Log source job | `docker`, `varlogs` |
| `host` | Host machine | `ctr01` |
| `container` | Container name | `traefik`, `grafana` |
| `image` | Docker image | `traefik:v3.6` |
| `compose_service` | Compose service name | `grafana` |
| `compose_project` | Compose project name | `monitoring` |

### List Available Labels

```logql
# In Grafana Explore, use Label browser
# Or query for unique values:
{job="docker"} | label_values(container)
```

---

## Configuration

### Loki Config

`config/loki/loki.yaml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

# 30-day retention
limits_config:
  retention_period: 720h
  max_query_lookback: 720h

compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
```

### Promtail Config

`config/promtail/promtail.yaml`:

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Docker container logs via Docker SD
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        regex: /(.*)
        target_label: container
      - source_labels: [__meta_docker_container_label_com_docker_compose_service]
        target_label: compose_service
      - source_labels: [__meta_docker_container_label_com_docker_compose_project]
        target_label: compose_project

  # System logs
  - job_name: varlogs
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*.log
```

### Data Location

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/monitoring/loki` | Log chunks and index |
| `/mnt/synology/docker/monitoring/promtail/positions` | Promtail position tracking |
| `config/loki/loki.yaml` | Loki configuration |
| `config/promtail/promtail.yaml` | Promtail configuration |

---

## Retention

Logs are retained for **30 days** (720 hours).

### How Retention Works

1. Loki's compactor runs every 10 minutes
2. Chunks older than `retention_period` are marked for deletion
3. After `retention_delete_delay` (2 hours), chunks are deleted

### Adjusting Retention

Edit `config/loki/loki.yaml`:

```yaml
limits_config:
  retention_period: 336h   # 14 days
  max_query_lookback: 336h

table_manager:
  retention_period: 336h
```

Restart Loki: `docker compose restart loki`

!!! warning "Storage Considerations"
    Longer retention = more disk usage. Monitor `/mnt/synology/docker/monitoring/loki` size.

---

## Troubleshooting

### No Logs Appearing

1. **Check Promtail is running:**
   ```bash
   ssh ctr01 'docker ps | grep promtail'
   ```

2. **Check Promtail can reach Loki:**
   ```bash
   ssh ctr01 'docker exec promtail wget -qO- http://loki:3100/ready'
   ```

3. **View Promtail logs:**
   ```bash
   ssh ctr01 'docker logs promtail --tail 50'
   ```

4. **Check Promtail targets:**
   ```bash
   ssh ctr01 'docker exec promtail wget -qO- http://localhost:9080/targets | jq .'
   ```

### Container Logs Missing

1. **Check container is running:** Promtail only discovers running containers

2. **Check container logging driver:**
   ```bash
   ssh ctr01 'docker inspect <container> --format "{{.HostConfig.LogConfig.Type}}"'
   ```
   Must be `json-file` (default). Containers using `none` or `syslog` won't work.

3. **Check Promtail position file:**
   ```bash
   ssh ctr01 'cat /mnt/synology/docker/monitoring/promtail/positions/positions.yaml'
   ```

### Query Timeout

1. **Reduce time range:** Query smaller windows
2. **Add label selectors:** Filter by container or job
3. **Use stream selectors first:** `{container="x"}` before `|= "text"`

### High Disk Usage

1. **Check Loki data size:**
   ```bash
   ssh ctr01 'du -sh /mnt/synology/docker/monitoring/loki'
   ```

2. **Reduce retention period**

3. **Exclude noisy containers:**
   Add drop rules to Promtail config for high-volume, low-value logs

### Loki Not Ready

```bash
# Check Loki health
ssh ctr01 'curl -s http://localhost:3100/ready'

# Check Loki logs
ssh ctr01 'docker logs loki --tail 100'

# Common issues:
# - Filesystem permissions on /loki
# - Out of disk space
# - Corrupted index (delete /loki and restart)
```

---

## Adding Log Sources

### Docker Container (Automatic)

All Docker containers on ctr01 are automatically discovered by Promtail. No configuration needed.

### System Logs

Add to Promtail `scrape_configs`:

```yaml
- job_name: syslog
  static_configs:
    - targets: [localhost]
      labels:
        job: syslog
        host: ctr01
        __path__: /var/log/syslog
```

### Remote Syslog (UDP)

Vector receives syslog on UDP port 5514 and forwards to Loki.

Configure devices to send syslog to `ctr01:5514`.

---

## Useful Queries Reference

| Purpose | Query |
|---------|-------|
| All errors | `{job="docker"} \|~ "(?i)error"` |
| Specific container | `{container="traefik"}` |
| By compose project | `{compose_project="monitoring"}` |
| HTTP 5xx errors | `{container="traefik"} \| json \| OriginStatus >= 500` |
| Last N lines | `{container="x"} \| tail 50` |
| Count by container | `sum by(container) (count_over_time({job="docker"}[1h]))` |
| Log rate | `sum(rate({job="docker"}[5m]))` |
| Exclude health checks | `{container="traefik"} != "/health"` |

---

## Related

- [Monitoring Stack](../stacks/ctr01.md#monitoring)
- [Grafana](grafana.md) - Query logs in Explore
- [Prometheus](prometheus.md) - Metrics collection
- [Loki Docs](https://grafana.com/docs/loki/latest/)
- [LogQL Reference](https://grafana.com/docs/loki/latest/logql/)
