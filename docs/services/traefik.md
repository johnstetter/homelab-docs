# Traefik

Traefik reverse proxy for routing and SSL termination across all services.

## Access

| Property | Value |
|----------|-------|
| **Dashboard** | [traefik.rsdn.io](https://traefik.rsdn.io) |
| **Stack** | [compose-stacks/core](https://gitlab.com/stetter-homelab/compose-stacks/core) |
| **Ports** | 80 (HTTP), 443 (HTTPS) |
| **Image** | `traefik:v3.6` |

## Authentication

The dashboard uses Traefik's built-in basic auth middleware.

**Credentials:** Check `.env` in the core stack or your password manager.

---

## Dashboard

The Traefik dashboard at [traefik.rsdn.io](https://traefik.rsdn.io) shows:

- **Routers** - All configured routes and their status
- **Services** - Backend services and health
- **Middlewares** - Active middleware chains
- **Entrypoints** - Listening ports (web:80, websecure:443)

### Quick Health Check

1. Visit [traefik.rsdn.io](https://traefik.rsdn.io)
2. Check "HTTP Routers" for green status indicators
3. Verify your service appears in the list

---

## Common Operations

### Add a New Docker Service

Add Traefik labels to your `compose.yml`:

```yaml
services:
  myapp:
    image: myapp:latest
    networks:
      - traefik_proxy
    labels:
      - traefik.enable=true
      - traefik.http.routers.myapp.rule=Host(`myapp.rsdn.io`)
      - traefik.http.routers.myapp.entrypoints=websecure
      - traefik.http.routers.myapp.tls.certresolver=cloudflare
      - traefik.http.services.myapp.loadbalancer.server.port=8080

networks:
  traefik_proxy:
    external: true
```

**Required labels:**
- `traefik.enable=true` - Expose to Traefik
- `traefik.http.routers.<name>.rule` - Host matching rule
- `traefik.http.routers.<name>.entrypoints=websecure` - HTTPS only
- `traefik.http.routers.<name>.tls.certresolver=cloudflare` - SSL cert
- `traefik.http.services.<name>.loadbalancer.server.port` - Container port

### Add a Non-Docker Service

Edit `config/traefik/dynamic.yml`:

```yaml
http:
  routers:
    myservice:
      rule: "Host(`myservice.rsdn.io`)"
      entryPoints:
        - websecure
      service: myservice
      tls:
        certResolver: cloudflare

  services:
    myservice:
      loadBalancer:
        servers:
          - url: "http://192.168.1.100:8080"
```

Traefik watches this file and applies changes automatically.

### Add Basic Auth to a Service

```yaml
labels:
  # ... existing labels ...
  - traefik.http.routers.myapp.middlewares=myapp-auth
  - traefik.http.middlewares.myapp-auth.basicauth.users=${MYAPP_AUTH}
```

Generate the auth string:
```bash
# Install htpasswd (apache2-utils)
htpasswd -nb username password
# Output: username:$apr1$...

# Add to .env
MYAPP_AUTH=username:$$apr1$$...  # Double $$ for Docker Compose
```

### Add Rate Limiting

```yaml
labels:
  - traefik.http.routers.myapp.middlewares=myapp-ratelimit
  - traefik.http.middlewares.myapp-ratelimit.ratelimit.average=100
  - traefik.http.middlewares.myapp-ratelimit.ratelimit.burst=50
```

### Check Route Configuration

```bash
# View all routers
ssh ctr01 'curl -s http://localhost:8080/api/http/routers | jq .'

# Check specific router
ssh ctr01 'curl -s http://localhost:8080/api/http/routers | jq ".[] | select(.name | contains(\"myapp\"))"'
```

---

## SSL Certificates

### How It Works

Traefik uses Let's Encrypt with Cloudflare DNS challenge:

1. New service with `tls.certresolver=cloudflare` triggers cert request
2. Traefik creates DNS TXT record via Cloudflare API
3. Let's Encrypt validates and issues wildcard cert
4. Cert stored in `/acme.json`

### Certificate Storage

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/core/traefik/acme.json` | Certificate storage (600 permissions) |

### Force Certificate Renewal

```bash
# Backup current certs
ssh ctr01 'cp /mnt/synology/docker/core/traefik/acme.json /mnt/synology/docker/core/traefik/acme.json.bak'

# Remove specific cert (Traefik will re-request)
# Or restart Traefik to trigger renewal check
ssh ctr01 'cd /opt/stacks/core && docker compose restart traefik'
```

### View Current Certificates

```bash
# Check acme.json (requires jq)
ssh ctr01 'cat /mnt/synology/docker/core/traefik/acme.json | jq ".cloudflare.Certificates[].domain"'
```

---

## Configuration

### Static Configuration

`config/traefik/traefik.yml` - Loaded at startup:

```yaml
log:
  level: INFO
  format: json

api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure  # Auto-redirect HTTP → HTTPS

  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false
    network: traefik_proxy
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true

certificatesResolvers:
  cloudflare:
    acme:
      dnsChallenge:
        provider: cloudflare
      email: "john@stetter.io"
      storage: /acme.json
```

### Dynamic Configuration

`config/traefik/dynamic.yml` - Hot-reloaded for non-Docker services.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLOUDFLARE_DNS_API_TOKEN` | Cloudflare API for DNS challenge |
| `DOMAIN` | Base domain (rsdn.io) |

---

## Logs

### Access Logs

```bash
# View recent access logs
ssh ctr01 'tail -100 /mnt/synology/docker/core/traefik/logs/access.log | jq .'

# Filter by service
ssh ctr01 'cat /mnt/synology/docker/core/traefik/logs/access.log | jq "select(.ServiceName | contains(\"grafana\"))"'
```

### Application Logs

```bash
# Traefik container logs
ssh ctr01 'docker logs traefik --tail 100'

# Follow logs
ssh ctr01 'docker logs traefik -f'
```

---

## Troubleshooting

### Service Returns 404

1. **Check router exists:** Visit dashboard, look for your router
2. **Verify Host rule:** Ensure domain matches exactly
3. **Check network:** Service must be on `traefik_proxy` network
4. **DNS configured?** Verify CNAME points to `rprx.rsdn.io`

### Service Returns 502

Backend is unreachable:

1. **Container running?** `docker ps | grep myapp`
2. **Correct port?** Check `loadbalancer.server.port` matches exposed port
3. **Health check?** Container might be starting
4. **Check logs:** `docker logs myapp`

### Certificate Errors

1. **Check Cloudflare token:** Verify `CLOUDFLARE_DNS_API_TOKEN` is valid
2. **Check acme.json permissions:** Must be 600
3. **Rate limited?** Let's Encrypt has rate limits; wait and retry
4. **View Traefik logs:** `docker logs traefik | grep -i acme`

### Dashboard Not Loading

```bash
# Check Traefik is running
docker ps | grep traefik

# Check ports
ss -tlnp | grep -E "80|443"

# Check container logs
docker logs traefik --tail 50
```

---

## Metrics

Traefik exports Prometheus metrics at `:8080/metrics`:

- `traefik_entrypoint_requests_total`
- `traefik_router_requests_total`
- `traefik_service_requests_total`

View in Grafana: [grafana.rsdn.io](https://grafana.rsdn.io) → Traefik dashboard

---

## Related

- [Core Stack](../stacks/ctr01.md#core)
- [Adding New Stacks](../runbooks/new-stack.md)
- [Traefik Official Docs](https://doc.traefik.io/traefik/)
- [Grafana](grafana.md) - Traefik metrics dashboard
