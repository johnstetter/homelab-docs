# Runbooks

Operational procedures and guides for managing the Stetter Homelab.

## Available Runbooks

### Deployment

| Runbook | Description |
|---------|-------------|
| [Adding New Stacks](new-stack.md) | Complete guide to deploying a new Docker Compose stack |

### Operations

| Runbook | Description |
|---------|-------------|
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

## Quick Reference

### Common Commands

#### Docker Operations

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs -f container-name

# Restart a container
docker restart container-name

# Execute command in container
docker exec -it container-name /bin/sh
```

#### Stack Operations

```bash
# Start a stack
cd /opt/stacks/stack-name
docker compose up -d

# Stop a stack
docker compose down

# View stack logs
docker compose logs -f

# Update stack
docker compose pull && docker compose up -d

# Restart a service
docker compose restart service-name
```

#### System Operations

```bash
# Check disk space
df -h

# Check memory usage
free -h

# View system logs
journalctl -f

# Check Docker disk usage
docker system df
```

### Emergency Procedures

#### Service Down

1. Check if container is running: `docker ps | grep service-name`
2. View container logs: `docker logs service-name`
3. Try restarting: `docker restart service-name`
4. Check Traefik routing: [traefik.rsdn.io](https://traefik.rsdn.io)
5. Check DNS resolution: `dig service.rsdn.io`

#### Host Unreachable

1. Check physical connectivity (power, network)
2. Try SSH from bastion (dev01)
3. Access via Proxmox console
4. Check system logs after recovery

#### Out of Disk Space

```bash
# Check what's using space
docker system df
df -h

# Clean up Docker
docker system prune -a --volumes

# Find large files
du -sh /* | sort -h
```

### Maintenance Windows

| Task | Schedule | Duration | Impact |
|------|----------|----------|--------|
| Container updates | Daily 4 AM | 15 min | Minimal |
| System updates | Weekly Sunday 3 AM | 30 min | Brief outage |
| Backup verification | Monthly | 1 hour | None |
| Full system backup | Weekly | 2 hours | None |

### Escalation

For issues that cannot be resolved with these runbooks:

1. Check service-specific documentation
2. Search GitHub/GitLab issues for similar problems
3. Check relevant Discord/Reddit communities
4. Open an issue in the appropriate repository

## Runbook Template

When creating new runbooks, use this template:

```markdown
# Runbook: [Title]

## Overview

Brief description of what this runbook covers.

## Prerequisites

- List of required access/tools
- Any pre-conditions

## Procedure

### Step 1: [Action]

Detailed instructions...

### Step 2: [Action]

Detailed instructions...

## Verification

How to verify the procedure was successful.

## Rollback

How to undo the changes if needed.

## Troubleshooting

Common issues and solutions.

## Related Documentation

Links to related docs.
```

## Related Documentation

- [Architecture Overview](../architecture/index.md)
- [Stack Overview](../stacks/index.md)
- [Service Catalog](../services/index.md)
