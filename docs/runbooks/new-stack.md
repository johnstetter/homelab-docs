# Adding New Stacks

Complete guide to deploying a new Docker Compose stack to ctr01.

## Prerequisites

- SSH access to ctr01
- GitLab access to `stetter-homelab` group
- `glab` CLI configured
- Access to Technitium DNS

## Quick Start

```bash
cd ~/projects/stetter-homelab/stack-template
./create-stack.sh my-stack
```

This creates a new stack from the template with CI/CD, Renovate, and Traefik pre-configured.

---

## Full Workflow

### Step 1: Create Stack from Template

```bash
cd ~/projects/stetter-homelab/stack-template
./create-stack.sh paperless
```

This creates `../compose-stacks/paperless/` with:

| File | Purpose |
|------|---------|
| `compose.yml` | Docker Compose with Traefik labels |
| `.gitlab-ci.yml` | CI/CD pipeline |
| `.env.example` | Environment variable template |
| `renovate.json` | Automated dependency updates |
| `CLAUDE.md` | Claude Code guidance |
| `README.md` | Stack documentation |

### Step 2: Create GitLab Repository

```bash
glab repo create stetter-homelab/compose-stacks/paperless --private
```

### Step 3: Push to GitLab

```bash
cd ~/projects/stetter-homelab/compose-stacks/paperless
git remote add origin git@gitlab.com:stetter-homelab/compose-stacks/paperless.git
git push -u origin main
```

### Step 4: Configure Your Stack

Edit the following files:

=== "compose.yml"

    ```yaml
    services:
      paperless:
        image: ghcr.io/paperless-ngx/paperless-ngx:latest
        container_name: paperless
        restart: always
        environment:
          - TZ=${TZ:-America/Chicago}
        volumes:
          - /mnt/synology/docker/paperless/data:/usr/src/paperless/data
          - /mnt/synology/docker/paperless/media:/usr/src/paperless/media
        networks:
          - traefik_proxy
        labels:
          - traefik.enable=true
          - traefik.http.routers.paperless.rule=Host(`paperless.${DOMAIN}`)
          - traefik.http.routers.paperless.entrypoints=websecure
          - traefik.http.routers.paperless.tls.certresolver=cloudflare
          - traefik.http.services.paperless.loadbalancer.server.port=8000

    networks:
      traefik_proxy:
        external: true
    ```

=== ".env.example"

    ```bash
    # Domain
    DOMAIN=rsdn.io
    TZ=America/Chicago

    # Service-specific
    PAPERLESS_SECRET_KEY=changeme
    ```

### Step 5: Create Data Directory on Synology

```bash
ssh ctr01 'sudo mkdir -p /mnt/synology/docker/paperless'
```

!!! note "Volume Strategy"
    All persistent data goes on NFS at `/mnt/synology/docker/<stack>/`. This enables:

    - Centralized backups via Synology Hyper Backup
    - Easy migration between hosts
    - 10G network performance

### Step 6: Clone to ctr01

```bash
ssh ctr01 'git clone git@gitlab.com:stetter-homelab/compose-stacks/paperless.git /opt/stacks/paperless'
```

### Step 7: Create .env File on ctr01

```bash
ssh ctr01 'cp /opt/stacks/paperless/.env.example /opt/stacks/paperless/.env'
ssh ctr01 'vim /opt/stacks/paperless/.env'  # Edit with real values
```

!!! warning "Never Commit Secrets"
    The `.env` file contains secrets and is gitignored. Always create it manually on the host.

### Step 8: Add DNS Record

Add a CNAME record in Technitium pointing to `rprx.rsdn.io`:

=== "Via Web UI"

    1. Go to [dns.rsdn.io](https://dns.rsdn.io)
    2. Select zone `rsdn.io`
    3. Add Record → CNAME
    4. Name: `paperless`
    5. CNAME: `rprx.rsdn.io`

=== "Via API"

    ```bash
    curl "http://192.168.1.4:5380/api/zones/records/add?\
    token=TOKEN&zone=rsdn.io&type=CNAME&\
    domain=paperless.rsdn.io&cname=rprx.rsdn.io&ttl=3600"
    ```

### Step 9: Start the Stack

```bash
ssh ctr01 'cd /opt/stacks/paperless && docker compose up -d'
```

### Step 10: Enable CI/CD Deployment

Edit `.gitlab-ci.yml` and uncomment the deploy section:

```yaml
include:
  - project: 'stetter-homelab/ci-templates'
    ref: v1.9.0
    file:
      - '/security.yml'
      - '/docker-compose-lint.yml'
      - '/deploy-stack.yml'  # Uncomment this
      - '/yamllint.yml'

stages:
  - security
  - validate
  - deploy  # Uncomment this

deploy:
  extends: .deploy-stack-auto  # Uncomment this
```

Commit and push to trigger automatic deployments on merge to main.

---

## Verification

### Check Container Status

```bash
ssh ctr01 'docker ps | grep paperless'
```

### Check Logs

```bash
ssh ctr01 'cd /opt/stacks/paperless && docker compose logs -f'
```

### Test Web Access

```bash
curl -I https://paperless.rsdn.io
```

### Verify in Traefik Dashboard

Visit [traefik.rsdn.io](https://traefik.rsdn.io) and check that the router appears.

---

## Rollback

If something goes wrong:

```bash
# Stop the stack
ssh ctr01 'cd /opt/stacks/paperless && docker compose down'

# Revert to previous commit
ssh ctr01 'cd /opt/stacks/paperless && git checkout HEAD~1'

# Restart
ssh ctr01 'cd /opt/stacks/paperless && docker compose up -d'
```

---

## Checklist

Use this checklist when adding a new stack:

- [ ] Create stack from template
- [ ] Create GitLab repository
- [ ] Push initial commit
- [ ] Configure compose.yml with services
- [ ] Create data directories on Synology
- [ ] Clone to ctr01
- [ ] Create .env file with secrets
- [ ] Add DNS record in Technitium
- [ ] Start stack and verify
- [ ] Enable CI/CD deployment
- [ ] Update [Service Catalog](../services/index.md)
- [ ] Update [ctr01 Stacks](../stacks/ctr01.md)

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs service-name

# Common issues:
# - Missing .env file
# - Volume mount doesn't exist
# - Port already in use
```

### 502 Bad Gateway

Traefik can't reach the backend:

1. Check container is running: `docker ps`
2. Check container is on `traefik_proxy` network
3. Verify port in Traefik labels matches exposed port
4. Check container logs for startup errors

### DNS Not Resolving

```bash
# Test resolution
dig paperless.rsdn.io

# Check Technitium
# - Is the record created?
# - Is it pointing to rprx.rsdn.io?
```

### Certificate Issues

Traefik handles certificates automatically. If you see cert errors:

1. Check Traefik logs: `docker logs traefik`
2. Verify Cloudflare API token in core stack `.env`
3. Wait a few minutes for Let's Encrypt

---

## Related Documentation

- [Stack Template README](https://gitlab.com/stetter-homelab/stack-template)
- [ctr01 Stacks](../stacks/ctr01.md)
- [Service Catalog](../services/index.md)
- [Troubleshooting](troubleshooting.md)
