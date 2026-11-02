# Traefik

The single reverse proxy for every `*.rsdn.io` name. (`stetter.io` no longer runs here: it's served by Cloudflare Workers.)

| Property | Value |
|----------|-------|
| **Dashboard** | [traefik.rsdn.io](https://traefik.rsdn.io) (Authentik, `Homelab Admins` only) |
| **Stack** | [compose-stacks/core](https://gitlab.com/stetter-homelab/compose-stacks/core) on ctr01 |
| **Image** | `traefik:v3.7` (digest-pinned, Renovate) |
| **DNS name** | `rprx.rsdn.io` → 192.168.1.20; services CNAME to it |
| **Ports** | 80 `web`, 443 `websecure` |

## Entrypoints

Traefik matches on SNI/`Host`, not DNS, so anyone who can reach an entrypoint can reach every router on it by guessing hostnames. Nothing is internet-facing: the UDM Pro forwards no ports (since 2026-11-02), and remote access is Tailscale, with the UDM Pro's WireGuard VPN as a backup.

| Entrypoint | Port | Reachable from | Use |
|------------|------|----------------|-----|
| `web` | 80 | LAN | Permanent redirect to `websecure` |
| `websecure` | 443 | LAN, tailnet, WireGuard | Every router |

`websecure` uses the `cloudflare` resolver with a wildcard `rsdn.io` / `*.rsdn.io` certificate (DNS-01, so nothing needs port 80 from outside), and trusts `X-Forwarded-*` only from loopback, the LAN and Docker networks. See [Network Topology](../architecture/network.md#reverse-proxy-traefik).

## Add a Docker Service

```yaml
services:
  myapp:
    image: myapp:1.2.3
    networks: [traefik_proxy]
    labels:
      - traefik.enable=true
      - traefik.http.routers.myapp.rule=Host(`myapp.rsdn.io`)
      - traefik.http.routers.myapp.entrypoints=websecure
      - traefik.http.services.myapp.loadbalancer.server.port=8080
      # optional: admin-only behind Authentik
      # - traefik.http.routers.myapp.middlewares=authentik@docker
      - flame.type=application
      - flame.name=My App
      - flame.url=https://myapp.rsdn.io

networks:
  traefik_proxy:
    external: true
```

The entrypoints already set TLS and the cert resolver, so routers don't need `tls.certresolver`. Then add a DNS CNAME `myapp.rsdn.io → rprx.rsdn.io` in Technitium on the NAS.

**Sharing with someone outside the house:** invite them to the tailnet. There is no public entrypoint, and adding one would put every router a guessed hostname away from the internet.

## Add a Non-Docker Backend

Edit `config/traefik/dynamic.yml` in the core repo and merge. The `config/traefik/` directory is mounted (not the single file), so the file provider picks up the change after the deploy's `git reset` with no restart.

```yaml
http:
  routers:
    myservice:
      rule: "Host(`myservice.rsdn.io`)"
      entryPoints: [websecure]
      service: myservice
  services:
    myservice:
      loadBalancer:
        servers:
          - url: "http://192.168.1.95:8080"
```

Use `serversTransport: insecure` for backends with self-signed certs (Proxmox, DSM, UniFi, the GitLab VM).

Current file-provider routes: Open WebUI and Hermes on the Studio, GitLab VM, Home Assistant, both Proxmox UIs, DSM, UniFi, both Technitium UIs, Pi-hole.

!!! note "Studio backends are pf-filtered"
    Open WebUI (:8080) and Hermes (:9119) only accept connections from ctr01 and loopback. If ctr01's IP changes, update `TRAEFIK_IP` in mac-config's `setup.sh` and re-run it.

## Authentication

`authentik@docker` is the forward-auth middleware from the [authentik](authentik.md) stack. Each protected app also needs a proxy provider and application in an Authentik blueprint. If Authentik is down, protected routers fail, so keep it to admin UIs.

The dashboard used to rely on a `lan-only` IP allowlist; that can't tell a tailnet client from a LAN client, because tailnet traffic arrives through the subnet router SNATed to a 192.168.1.x address.

## Certificates

```bash
ssh ctr01 'sudo jq -r ".cloudflare.Certificates[].domain" /mnt/synology/docker/core/traefik/acme.json'
docker logs traefik 2>&1 | grep -i acme
```

`acme.json` must stay mode 600. The Cloudflare token is `CLOUDFLARE_DNS_API_TOKEN` in the core stack's `.env`.

## Logs and Metrics

- Access log (JSON) and Traefik log: `/mnt/synology/docker/core/traefik/logs/`, also `docker logs traefik`.
- Prometheus scrapes `traefik:8080` over `monitoring_external`, with entrypoint, router and service labels.
- Tracing to Jaeger was removed in October 2026.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| 404 | Router exists on the dashboard? Host rule exact? Container on `traefik_proxy`? |
| 502 / 504 | Backend up? Right `loadbalancer.server.port`? For Studio backends, is the daemon up and the pf anchor allowing ctr01? |
| Works on LAN, not remotely | Client on the tailnet (or WireGuard)? Split DNS resolving `rsdn.io` to 192.168.1.4? |
| Dashboard errors | Authentik down: `docker ps | grep authentik` |
| `dynamic.yml` change ignored | YAML error: `docker logs traefik | grep -i error` |
| Static config change ignored | `traefik.yml` is read at startup. Core's deploy restarts Traefik when it changes (`RESTART_ON_CHANGE`, ci-templates v1.14.0); by hand: `docker compose restart traefik` |
