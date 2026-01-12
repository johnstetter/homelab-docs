# Portainer

Docker container management UI for visual container operations.

## Access

| Property | Value |
|----------|-------|
| **URL** | [portainer.rsdn.io](https://portainer.rsdn.io) |
| **Stack** | [compose-stacks/management](https://gitlab.com/stetter-homelab/compose-stacks/management) |
| **Port** | 9000 |
| **Image** | `portainer/portainer-ee:2.33.6` |

## Authentication

Portainer uses its own user database.

**Initial setup:** First access prompts for admin account creation.

---

## Common Operations

### View Running Containers

1. Go to [portainer.rsdn.io](https://portainer.rsdn.io)
2. Select **local** environment
3. Click **Containers** in the sidebar

### View Container Logs

1. Navigate to **Containers**
2. Click container name
3. Click **Logs** tab
4. Toggle **Auto-refresh** for live logs

### Restart a Container

1. Navigate to **Containers**
2. Check the container checkbox
3. Click **Restart** button

Or click container → **Restart** in the container detail view.

### Stop/Start a Container

1. Navigate to **Containers**
2. Select container(s)
3. Click **Stop** or **Start**

### View Container Stats

1. Click container name
2. Click **Stats** tab
3. View CPU, memory, network, I/O in real-time

### Execute Commands in Container

1. Click container name
2. Click **Console** tab
3. Select shell (`/bin/sh` or `/bin/bash`)
4. Click **Connect**

### Deploy a Stack

1. Go to **Stacks** → **Add stack**
2. Choose method:
   - **Web editor** - Paste compose YAML
   - **Upload** - Upload compose file
   - **Git repository** - Clone from repo
3. Add environment variables
4. Click **Deploy the stack**

!!! note "Prefer CLI Deployment"
    For production stacks, use CLI deployment via git for version control.
    Portainer is useful for quick testing and debugging.

### Update a Container Image

1. Navigate to **Containers**
2. Click container name
3. Click **Recreate** button
4. Enable **Pull latest image**
5. Click **Recreate**

---

## Stacks vs Containers

| Concept | Description |
|---------|-------------|
| **Container** | Single running container |
| **Stack** | Group of containers from one compose file |

Portainer shows containers deployed via `docker compose` but can't manage them as stacks unless deployed through Portainer.

---

## Environment Management

### Add Remote Docker Host

1. Go to **Environments** → **Add environment**
2. Choose **Docker Standalone**
3. Select connection method:
   - **Agent** (recommended) - Install Portainer agent
   - **Socket** - Direct socket access
   - **API** - Docker API over TCP

### Agent Installation

On the remote host:
```bash
docker run -d -p 9001:9001 --name portainer_agent \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes \
  portainer/agent:latest
```

Then add environment with agent URL: `<host-ip>:9001`

---

## Registry Management

### Add Private Registry

1. Go to **Registries** → **Add registry**
2. Choose registry type (Docker Hub, GitLab, custom)
3. Enter credentials
4. Save

### Pull from Private Registry

When deploying, specify full image path:
```yaml
image: registry.gitlab.com/stetter-homelab/myimage:latest
```

---

## Configuration

### Data Location

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/management/portainer/data` | Portainer database and settings |

### Portainer Features

- **Edge Agents** - Manage remote Docker hosts
- **GitOps** - Deploy stacks from Git repos
- **RBAC** - Role-based access control (EE)
- **Activity Logs** - Audit trail of actions

---

## Troubleshooting

### Can't Connect to Docker

```bash
# Check Docker socket permissions
ls -la /var/run/docker.sock

# Verify Portainer can access socket
docker exec portainer ls -la /var/run/docker.sock
```

### Stack Won't Deploy

1. Check compose YAML syntax
2. Verify environment variables are set
3. Check container logs for errors
4. Ensure required networks exist

### Slow UI Performance

1. Clear browser cache
2. Reduce log history retention
3. Check container count (many containers = slower)

### Lost Admin Password

```bash
# Reset admin password
docker exec portainer /portainer --admin-password-file /tmp/password

# Or recreate container with new password hash
```

---

## Alternative: Dozzle

For **log viewing only**, Dozzle is lighter weight:

| Feature | Portainer | Dozzle |
|---------|-----------|--------|
| Container logs | Yes | Yes (optimized) |
| Container management | Yes | No |
| Stack deployment | Yes | No |
| Resource usage | Higher | Lower |

Access Dozzle at [dozzle.rsdn.io](https://dozzle.rsdn.io)

---

## Related

- [Management Stack](../stacks/ctr01.md#management)
- [Dozzle](https://dozzle.dev/)
- [Portainer Docs](https://docs.portainer.io/)
