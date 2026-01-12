# Prometheus

Metrics collection and alerting for homelab infrastructure.

## Access

| Property | Value |
|----------|-------|
| **URL** | [prometheus.rsdn.io](https://prometheus.rsdn.io) |
| **Stack** | [compose-stacks/monitoring](https://gitlab.com/stetter-homelab/compose-stacks/monitoring) |
| **Port** | 9090 |
| **Image** | `prom/prometheus:v3.8.1` |

## Authentication

No authentication configured. Access is restricted via Traefik and network segmentation.

---

## Dashboard

The Prometheus UI at [prometheus.rsdn.io](https://prometheus.rsdn.io) provides:

- **Graph** - Ad-hoc query execution and visualization
- **Alerts** - Current alerting rule status
- **Status** - Targets, configuration, and runtime info
- **TSDB Status** - Database statistics

### Quick Health Check

1. Visit [prometheus.rsdn.io/targets](https://prometheus.rsdn.io/targets)
2. Verify all targets show **UP** status
3. Check for any targets in **DOWN** state

---

## Common PromQL Queries

### System Metrics (Node Exporter)

**CPU Usage:**
```promql
# CPU usage percentage by host (all cores averaged)
100 - (avg by(host) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPU usage per core
100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)

# Top 5 hosts by CPU usage
topk(5, 100 - (avg by(host) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))
```

**Memory Usage:**
```promql
# Memory usage percentage by host
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Available memory in GB
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# Used memory in GB
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024

# Memory usage on specific host
(1 - (node_memory_MemAvailable_bytes{host="ctr01"} / node_memory_MemTotal_bytes{host="ctr01"})) * 100
```

**Disk Space:**
```promql
# Disk usage percentage (excluding virtual filesystems)
(
  (node_filesystem_size_bytes{fstype!~"tmpfs|overlay|shm|nfs.*"} - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay|shm|nfs.*"})
  / node_filesystem_size_bytes{fstype!~"tmpfs|overlay|shm|nfs.*"}
) * 100

# Available disk space in GB
node_filesystem_avail_bytes{fstype!~"tmpfs|overlay|shm"} / 1024 / 1024 / 1024

# Root filesystem usage by host
(
  (node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"})
  / node_filesystem_size_bytes{mountpoint="/"}
) * 100
```

**Disk I/O:**
```promql
# Disk read bytes per second
rate(node_disk_read_bytes_total[5m])

# Disk write bytes per second
rate(node_disk_written_bytes_total[5m])

# Disk I/O utilization (percentage of time busy)
rate(node_disk_io_time_seconds_total[5m]) * 100
```

**Network Throughput:**
```promql
# Network receive rate (bytes/sec)
rate(node_network_receive_bytes_total{device!~"lo|veth.*|br-.*|docker.*"}[5m])

# Network transmit rate (bytes/sec)
rate(node_network_transmit_bytes_total{device!~"lo|veth.*|br-.*|docker.*"}[5m])

# Total network traffic by host (Mbps)
(
  sum by(host) (rate(node_network_receive_bytes_total{device!~"lo|veth.*"}[5m]))
  + sum by(host) (rate(node_network_transmit_bytes_total{device!~"lo|veth.*"}[5m]))
) * 8 / 1024 / 1024
```

**System Load:**
```promql
# 1-minute load average
node_load1

# Load per CPU core
node_load1 / count without(cpu) (node_cpu_seconds_total{mode="idle"})

# System uptime in days
node_time_seconds - node_boot_time_seconds / 86400
```

---

### Docker/Container Metrics (cAdvisor)

**Container CPU Usage:**
```promql
# CPU usage by container name
sum by(name) (rate(container_cpu_usage_seconds_total{name!=""}[5m])) * 100

# Top 10 containers by CPU
topk(10, sum by(name) (rate(container_cpu_usage_seconds_total{name!=""}[5m])) * 100)

# CPU usage for specific container
sum(rate(container_cpu_usage_seconds_total{name="ollama"}[5m])) * 100
```

**Container Memory Usage:**
```promql
# Memory usage by container (MB)
sum by(name) (container_memory_usage_bytes{name!=""}) / 1024 / 1024

# Memory usage percentage (if limit set)
(container_memory_usage_bytes{name!=""} / container_spec_memory_limit_bytes{name!=""}) * 100

# Top 10 containers by memory
topk(10, sum by(name) (container_memory_usage_bytes{name!=""}) / 1024 / 1024)

# Containers using more than 1GB
container_memory_usage_bytes{name!=""} > 1073741824
```

**Container Restart Counts:**
```promql
# Container restarts in last hour
increase(container_restart_count{name!=""}[1h])

# Containers that restarted recently
container_restart_count{name!=""} > 0

# Total restart count by container
sum by(name) (container_restart_count{name!=""})
```

**Container Network Traffic:**
```promql
# Network receive by container (bytes/sec)
sum by(name) (rate(container_network_receive_bytes_total{name!=""}[5m]))

# Network transmit by container (bytes/sec)
sum by(name) (rate(container_network_transmit_bytes_total{name!=""}[5m]))

# Top 5 containers by network traffic
topk(5, sum by(name) (
  rate(container_network_receive_bytes_total{name!=""}[5m])
  + rate(container_network_transmit_bytes_total{name!=""}[5m])
))
```

**Container Disk I/O:**
```promql
# Disk read by container
sum by(name) (rate(container_fs_reads_bytes_total{name!=""}[5m]))

# Disk write by container
sum by(name) (rate(container_fs_writes_bytes_total{name!=""}[5m]))
```

---

### Traefik Metrics

**Request Rate:**
```promql
# Total requests per second
sum(rate(traefik_service_requests_total[5m]))

# Requests per service
sum by(service) (rate(traefik_service_requests_total[5m]))

# Top 10 services by request rate
topk(10, sum by(service) (rate(traefik_service_requests_total[5m])))
```

**Error Rates:**
```promql
# 5xx errors per service
sum by(service) (rate(traefik_service_requests_total{code=~"5.."}[5m]))

# 4xx errors per service
sum by(service) (rate(traefik_service_requests_total{code=~"4.."}[5m]))

# Error rate percentage by service
(
  sum by(service) (rate(traefik_service_requests_total{code=~"[45].."}[5m]))
  / sum by(service) (rate(traefik_service_requests_total[5m]))
) * 100

# Services with high error rate (>5%)
(
  sum by(service) (rate(traefik_service_requests_total{code=~"[45].."}[5m]))
  / sum by(service) (rate(traefik_service_requests_total[5m]))
) * 100 > 5
```

**Response Latency:**
```promql
# Average response time by service (seconds)
sum by(service) (rate(traefik_service_request_duration_seconds_sum[5m]))
/ sum by(service) (rate(traefik_service_request_duration_seconds_count[5m]))

# 95th percentile latency by service
histogram_quantile(0.95, sum by(service, le) (rate(traefik_service_request_duration_seconds_bucket[5m])))

# 99th percentile latency
histogram_quantile(0.99, sum by(service, le) (rate(traefik_service_request_duration_seconds_bucket[5m])))

# Slow services (avg > 1s)
(
  sum by(service) (rate(traefik_service_request_duration_seconds_sum[5m]))
  / sum by(service) (rate(traefik_service_request_duration_seconds_count[5m]))
) > 1
```

**Active Connections:**
```promql
# Open connections by entrypoint
traefik_entrypoint_open_connections

# Requests in flight
traefik_service_requests_total - traefik_service_requests_total offset 5m
```

---

### GPU Metrics (NVIDIA DCGM)

**GPU Utilization:**
```promql
# GPU utilization percentage
DCGM_FI_DEV_GPU_UTIL

# GPU memory utilization percentage
DCGM_FI_DEV_MEM_COPY_UTIL

# SM (Streaming Multiprocessor) utilization
DCGM_FI_PROF_SM_ACTIVE * 100
```

**GPU Memory:**
```promql
# Used GPU memory (MB)
DCGM_FI_DEV_FB_USED

# Free GPU memory (MB)
DCGM_FI_DEV_FB_FREE

# Total GPU memory (MB)
DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE

# GPU memory usage percentage
DCGM_FI_DEV_FB_USED / (DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE) * 100
```

**GPU Temperature:**
```promql
# GPU temperature (Celsius)
DCGM_FI_DEV_GPU_TEMP

# Memory temperature
DCGM_FI_DEV_MEMORY_TEMP

# Alert: GPU overheating (>80C)
DCGM_FI_DEV_GPU_TEMP > 80
```

**GPU Power:**
```promql
# Current power usage (Watts)
DCGM_FI_DEV_POWER_USAGE

# Power limit
DCGM_FI_DEV_ENFORCED_POWER_LIMIT
```

---

### Proxmox Metrics

**VM Status:**
```promql
# VM running status
pve_guest_info{type="qemu"}

# VM CPU usage
pve_cpu_usage_ratio{type="qemu"}

# VM memory usage
pve_memory_usage_bytes{type="qemu"}
```

**Host Resources:**
```promql
# Proxmox host CPU
pve_cpu_usage_ratio{type="node"}

# Proxmox host memory
pve_memory_usage_bytes{type="node"}

# Storage usage
pve_disk_usage_bytes
```

---

## Scrape Configuration

Prometheus scrapes targets defined in `config/prometheus/prometheus.yml`.

### Current Targets

| Job | Target | Interval | Purpose |
|-----|--------|----------|---------|
| `ctr01-node-exporter` | 192.168.1.20:9100 | 15s | Container host metrics |
| `nexus-node-exporter` | 192.168.1.12:9100 | 15s | Proxmox MS-A2 metrics |
| `pve-tc1-node-exporter` | 192.168.1.11:9100 | 15s | Proxmox TC1 metrics |
| `synology-node-exporter` | 192.168.1.4:9100 | 15s | NAS metrics |
| `homeassistant-node` | 192.168.1.3:9100 | 15s | HA VM metrics |
| `homeassistant-entities` | 192.168.1.3:8123 | 30s | HA entity metrics |
| `dcgm-exporter` | dcgm-exporter:9400 | 30s | NVIDIA GPU metrics |
| `cadvisor` | cadvisor:8080 | 30s | Container metrics |
| `traefik` | traefik:8080 | 15s | Reverse proxy metrics |
| `unpoller` | unpoller:9130 | 30s | UniFi network metrics |
| `proxmox-pve-tc1` | pve-exporter:9221 | 60s | PVE TC1 cluster metrics |
| `proxmox-nexus` | pve-exporter:9221 | 60s | PVE MS-A2 cluster metrics |

### Add a New Scrape Target

Edit `config/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "my-new-service"
    static_configs:
      - targets: ["192.168.1.100:9100"]
        labels:
          host: "my-host"
```

Restart Prometheus: `docker compose restart prometheus`

### Check Target Status

```bash
# View all targets
ssh ctr01 'curl -s http://localhost:9090/api/v1/targets | jq ".data.activeTargets[] | {job: .labels.job, health: .health}"'

# Check specific job
ssh ctr01 'curl -s http://localhost:9090/api/v1/targets | jq ".data.activeTargets[] | select(.labels.job == \"traefik\")"'
```

---

## Alerting

### Alert Rules

Alert rules are stored in `config/prometheus/rules/`.

**Current rules:**
- `disk-alerts.yml` - Disk space warnings and critical alerts

### Creating Alert Rules

Create a new file in `config/prometheus/rules/`:

```yaml
# config/prometheus/rules/container-alerts.yml
groups:
  - name: container-alerts
    rules:
      # Container down
      - alert: ContainerDown
        expr: absent(container_last_seen{name="traefik"})
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.name }} is down"
          description: "Container has not been seen for more than 1 minute"

      # High CPU usage
      - alert: ContainerHighCPU
        expr: sum by(name) (rate(container_cpu_usage_seconds_total[5m])) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.name }} high CPU"
          description: "Container is using {{ printf \"%.1f\" $value }}% CPU"

      # High memory usage
      - alert: ContainerHighMemory
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.name }} high memory"
          description: "Container is using {{ printf \"%.1f\" $value }}% of memory limit"
```

### Example Alert Rules

**Host Down:**
```yaml
- alert: HostDown
  expr: up{job=~".*-node-exporter"} == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Host {{ $labels.host }} is down"
    description: "Node exporter is not responding"
```

**High Load Average:**
```yaml
- alert: HighLoadAverage
  expr: node_load1 > count without(cpu) (node_cpu_seconds_total{mode="idle"}) * 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High load on {{ $labels.host }}"
    description: "Load average is {{ printf \"%.2f\" $value }}"
```

**GPU Overheating:**
```yaml
- alert: GPUOverheating
  expr: DCGM_FI_DEV_GPU_TEMP > 80
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "GPU temperature high"
    description: "GPU is at {{ printf \"%.0f\" $value }}C"
```

### Alertmanager

Alerts are sent to Alertmanager at `alertmanager:9093`, which routes to Telegram.

View active alerts: [alertmanager.rsdn.io](https://alertmanager.rsdn.io)

---

## Configuration

### Data Location

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/monitoring/prometheus` | Time series database (TSDB) |
| `config/prometheus/prometheus.yml` | Scrape configuration |
| `config/prometheus/rules/` | Alerting rules |

### Command Line Options

```yaml
command:
  - '--config.file=/etc/prometheus/prometheus.yml'
  - '--storage.tsdb.path=/prometheus'
  - '--storage.tsdb.retention.time=30d'    # Keep 30 days of data
```

### Environment Variables

No environment variables required. Prometheus uses file-based configuration.

---

## Troubleshooting

### Target Shows DOWN

1. **Check target is running:**
   ```bash
   ssh ctr01 'curl -s http://192.168.1.20:9100/metrics | head -5'
   ```

2. **Check network connectivity:**
   ```bash
   ssh ctr01 'docker exec prometheus wget -qO- http://192.168.1.20:9100/metrics | head -5'
   ```

3. **Verify firewall rules:** Ensure port is open on target host

### Query Returns No Data

1. **Check time range:** Metrics may not exist in selected range
2. **Verify metric name:** Use autocomplete in UI
3. **Check labels:** Filter may be too restrictive
4. **Check retention:** Data older than 30 days is deleted

### High Memory Usage

1. **Reduce retention:**
   ```yaml
   - '--storage.tsdb.retention.time=15d'
   ```

2. **Reduce scrape frequency:** Increase `scrape_interval`

3. **Limit targets:** Only scrape what you need

### Configuration Errors

```bash
# Check config syntax
ssh ctr01 'docker exec prometheus promtool check config /etc/prometheus/prometheus.yml'

# Check rules syntax
ssh ctr01 'docker exec prometheus promtool check rules /etc/prometheus/rules/*.yml'
```

---

## Backup

Prometheus data is backed up via Synology Hyper Backup.

**Data location:** `/mnt/synology/docker/monitoring/prometheus`

**Manual snapshot:**
```bash
# Create TSDB snapshot
ssh ctr01 'curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot'
```

---

## Related

- [Monitoring Stack](../stacks/ctr01.md#monitoring)
- [Grafana](grafana.md) - Visualization dashboards
- [Loki](loki.md) - Log aggregation
- [Alertmanager](https://alertmanager.rsdn.io) - Alert routing
- [Prometheus Docs](https://prometheus.io/docs/)
