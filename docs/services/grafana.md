# Grafana

Visualization and dashboards for metrics, logs, and traces.

## Access

| Property | Value |
|----------|-------|
| **URL** | [grafana.rsdn.io](https://grafana.rsdn.io) |
| **Stack** | [compose-stacks/monitoring](https://gitlab.com/stetter-homelab/compose-stacks/monitoring) |
| **Port** | 3000 |
| **Image** | `grafana/grafana:12.3.1` |

## Authentication

**Default admin:** Configured in monitoring stack `.env`

- Username: `GRAFANA_ADMIN_USER`
- Password: `GRAFANA_ADMIN_PASSWORD`

---

## Data Sources

Grafana is pre-configured with these data sources (via provisioning):

| Source | Type | URL | Purpose |
|--------|------|-----|---------|
| **Prometheus** | prometheus | `http://prometheus:9090` | Metrics (default) |
| **Loki** | loki | `http://loki:3100` | Logs |
| **InfluxDB (Home Assistant)** | influxdb | `http://192.168.1.3:8086` | Home Assistant history |

Data sources are managed via provisioning and cannot be edited in the UI.

---

## Common Operations

### View Dashboards

1. Go to [grafana.rsdn.io](https://grafana.rsdn.io)
2. Click **Dashboards** in the left sidebar
3. Browse or search for dashboards

**Key dashboards:**
- Docker Host Overview
- Traefik Metrics
- Node Exporter Full
- Loki Log Explorer

### Explore Metrics (Ad-hoc Queries)

1. Click **Explore** in the left sidebar
2. Select data source (Prometheus, Loki, etc.)
3. Build your query

**Example Prometheus queries:**
```promql
# CPU usage by container
rate(container_cpu_usage_seconds_total[5m])

# Memory usage
container_memory_usage_bytes

# HTTP requests by service
traefik_service_requests_total
```

### Explore Logs

1. Click **Explore** → Select **Loki**
2. Use LogQL to query:

```logql
# All logs from a container
{container_name="traefik"}

# Filter by content
{container_name="traefik"} |= "error"

# JSON parsing
{container_name="traefik"} | json | status >= 400
```

### Create a Dashboard

1. Click **Dashboards** → **New** → **New Dashboard**
2. Add panels with **+ Add visualization**
3. Select data source and build query
4. Save dashboard

!!! note "Provisioned Dashboards"
    Dashboards in `config/grafana/dashboards/` are read-only.
    Create new dashboards in the UI for editable versions.

### Import a Dashboard

1. Go to **Dashboards** → **New** → **Import**
2. Enter dashboard ID from [Grafana.com](https://grafana.com/grafana/dashboards/)
3. Select data source mappings
4. Click **Import**

**Recommended dashboards:**
- **1860** - Node Exporter Full
- **13946** - Docker Container Metrics
- **17346** - Traefik 3.x

### Create an Alert

1. Go to **Alerting** → **Alert rules** → **New alert rule**
2. Define query and condition
3. Set evaluation interval
4. Configure notification channel
5. Save

**Example alert (high CPU):**
```promql
avg(rate(container_cpu_usage_seconds_total{name="ollama"}[5m])) > 0.8
```

---

## Configuration

### Provisioning

Grafana uses file-based provisioning for reproducible configs:

```
config/grafana/
├── provisioning/
│   └── datasources/
│       └── default.yaml    # Data source definitions
└── dashboards/
    └── *.json              # Dashboard JSON files
```

### Data Location

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/monitoring/grafana` | Grafana data (SQLite DB, plugins) |
| `config/grafana/provisioning/` | Provisioned data sources |
| `config/grafana/dashboards/` | Provisioned dashboards |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `GRAFANA_ADMIN_USER` | Admin username |
| `GRAFANA_ADMIN_PASSWORD` | Admin password |
| `GF_SERVER_ROOT_URL` | External URL |
| `INFLUXDB_HA_TOKEN` | InfluxDB API token |

---

## Adding a Data Source

### Via Provisioning (Recommended)

Edit `config/grafana/provisioning/datasources/default.yaml`:

```yaml
datasources:
  - name: MyNewSource
    type: prometheus
    uid: my-source
    access: proxy
    url: http://my-service:9090
    isDefault: false
    editable: false
```

Restart Grafana: `docker compose restart grafana`

### Via UI (Temporary)

1. Go to **Connections** → **Data sources**
2. Click **Add data source**
3. Configure and test

!!! warning "UI-added sources aren't persistent"
    Data sources added via UI aren't in version control.
    Use provisioning for permanent sources.

---

## Adding Dashboards

### Via Provisioning

1. Export dashboard JSON from UI (Share → Export → Save to file)
2. Save to `config/grafana/dashboards/`
3. Commit and push
4. Restart Grafana

### Dashboard Provisioning Config

`config/grafana/provisioning/dashboards/default.yaml`:

```yaml
apiVersion: 1
providers:
  - name: 'default'
    folder: 'Provisioned'
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

---

## Troubleshooting

### Can't Login

1. Check credentials in `.env`
2. Reset admin password:
   ```bash
   docker exec grafana grafana-cli admin reset-admin-password newpassword
   ```

### Data Source Error

1. **Check container network:** Data sources use internal Docker DNS
2. **Verify service is running:** `docker ps | grep prometheus`
3. **Test connectivity:**
   ```bash
   docker exec grafana curl -s http://prometheus:9090/-/ready
   ```

### Dashboard Not Loading

1. **Check browser console** for JavaScript errors
2. **Check data source:** Verify Prometheus/Loki is healthy
3. **Check query:** Time range might have no data

### Provisioned Dashboard Shows "Read Only"

Expected behavior. Provisioned dashboards can't be edited in the UI.

To make editable:
1. Copy JSON from provisioned dashboard
2. Create new dashboard and paste JSON
3. Save as new dashboard

### Slow Queries

1. **Add time range filters** to queries
2. **Use recording rules** in Prometheus for expensive queries
3. **Limit series** with label filters

---

## Backup

Grafana data is backed up via Synology Hyper Backup.

**Manual export:**
```bash
# Export all dashboards
ssh ctr01 'docker exec grafana grafana-cli dashboards export --dir /tmp/dashboards'
```

**What's stored:**
- User accounts and permissions
- Non-provisioned dashboards
- Alerting rules
- Annotations

---

## Related

- [Monitoring Stack](../stacks/ctr01.md#monitoring)
- [Prometheus](prometheus.md)
- [Loki](loki.md)
- [Grafana Docs](https://grafana.com/docs/grafana/latest/)
