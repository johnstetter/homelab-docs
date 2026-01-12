# Troubleshooting

Common issues and solutions for the Stetter Homelab.

## Quick Diagnostics

### Health Check Commands

```bash
# Container status
ssh ctr01 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# System resources
ssh ctr01 'free -h && df -h /mnt/synology/docker'

# Network connectivity
ping -c 3 ctr01.rsdn.io
ping -c 3 syn.rsdn.io

# DNS resolution
dig traefik.rsdn.io
```

---

## Service Issues

### Container Won't Start

**Symptoms:** Container exits immediately or restart loops.

**Diagnosis:**

```bash
# Check container logs
docker logs container-name

# Check recent events
docker events --since 5m --filter container=container-name

# Inspect container
docker inspect container-name | jq '.[0].State'
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Missing .env file | `cp .env.example .env` and fill in values |
| Volume mount doesn't exist | `mkdir -p /mnt/synology/docker/stack/service` |
| Port already in use | `docker ps` to find conflict, stop other container |
| Image pull failed | `docker compose pull` to retry |
| Permission denied | Check NFS mount permissions |

### 502 Bad Gateway

**Symptoms:** Traefik shows 502 error when accessing service.

**Diagnosis:**

```bash
# Check if container is running
docker ps | grep service-name

# Check Traefik can reach container
docker exec traefik wget -qO- http://service-name:port/health

# Check container logs
docker logs service-name
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Container not running | `docker compose up -d` |
| Wrong network | Add `traefik_proxy` to compose.yml networks |
| Wrong port in labels | Match `loadbalancer.server.port` to actual port |
| Service still starting | Wait and check logs |
| Health check failing | Check application logs |

### 404 Not Found

**Symptoms:** Traefik returns 404 for a valid URL.

**Diagnosis:**

```bash
# Check Traefik dashboard for router
curl -s http://localhost:8080/api/http/routers | jq '.[] | select(.name | contains("service"))'

# Verify Host rule
docker inspect service-name | jq '.[0].Config.Labels'
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Missing Traefik labels | Add `traefik.enable=true` and router labels |
| Wrong Host rule | Check domain in `traefik.http.routers.X.rule` |
| DNS not configured | Add CNAME in Technitium |
| Traefik not reloaded | Wait or restart Traefik |

### SSL Certificate Errors

**Symptoms:** Browser shows certificate warning or invalid cert.

**Diagnosis:**

```bash
# Check Traefik logs for ACME errors
docker logs traefik 2>&1 | grep -i acme

# Verify certificate
echo | openssl s_client -connect service.rsdn.io:443 2>/dev/null | openssl x509 -noout -dates

# Check acme.json
ls -la /mnt/synology/docker/core/traefik/acme.json
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Rate limited by Let's Encrypt | Wait 1 hour, check Traefik logs |
| Cloudflare API token invalid | Check `CLOUDFLARE_DNS_API_TOKEN` in core .env |
| Wrong certresolver name | Use `cloudflare` in labels |
| acme.json permissions | `chmod 600 acme.json` |

---

## Network Issues

### Can't Reach Service from LAN

**Symptoms:** Service works via localhost but not from other machines.

**Diagnosis:**

```bash
# Test from another machine
curl -v https://service.rsdn.io

# Check DNS resolution
dig service.rsdn.io @192.168.1.4

# Check Traefik is listening
ssh ctr01 'ss -tlnp | grep -E "80|443"'
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| DNS not configured | Add CNAME pointing to rprx.rsdn.io |
| Firewall blocking | Check UFW: `ufw status` |
| Traefik not running | `docker ps | grep traefik` |
| Wrong bind address | Check Traefik ports in compose.yml |

### NFS Mount Issues

**Symptoms:** `/mnt/synology/docker` not accessible or stale.

**Diagnosis:**

```bash
# Check mount status
mount | grep synology
df -h /mnt/synology

# Test NFS connectivity
showmount -e 10.0.10.4

# Check for stale handles
ls /mnt/synology/docker 2>&1
```

**Solutions:**

```bash
# Remount NFS
sudo umount -f /mnt/synology/docker
sudo mount -a

# If stale NFS handle
sudo umount -l /mnt/synology/docker
sudo mount -a

# Check fstab entry
cat /etc/fstab | grep synology
```

### 10G Network Not Working

**Symptoms:** Slow NFS performance, using 1G instead of 10G.

**Diagnosis:**

```bash
# Check interface speed
ethtool eth1 | grep Speed

# Test bandwidth
iperf3 -c 10.0.10.4

# Verify MTU
ip link show eth1 | grep mtu
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Wrong interface | Check `ip addr` for 10.0.10.x address |
| MTU mismatch | Set MTU 9000 on both ends |
| Cable issue | Check SFP+ module and DAC cable |

---

## Storage Issues

### Disk Space Full

**Symptoms:** Containers failing, "no space left on device" errors.

**Diagnosis:**

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Find large files
du -sh /mnt/synology/docker/* | sort -h | tail -20

# Check container logs size
du -sh /var/lib/docker/containers/*/
```

**Solutions:**

```bash
# Clean Docker (safe)
docker system prune -f

# Clean Docker (aggressive - removes unused images)
docker system prune -a -f

# Clean old logs
truncate -s 0 /var/lib/docker/containers/*/*.log

# Remove old backups
find /mnt/synology/docker -name "*.bak" -mtime +30 -delete
```

### Database Corruption

**Symptoms:** Service fails with database errors.

**Diagnosis:**

```bash
# Check database logs
docker logs service-db

# For SQLite
sqlite3 database.db "PRAGMA integrity_check;"

# For PostgreSQL
docker exec postgres pg_isready
```

**Solutions:**

```bash
# Restore from backup (SQLite)
cp database.db database.db.corrupt
cp /backup/database.db.bak database.db

# Restore from backup (PostgreSQL)
docker exec -i postgres psql -U user db < backup.sql
```

---

## Host Issues

### Host Unreachable

**Symptoms:** Can't SSH to ctr01 or dev01.

**Diagnosis:**

1. Check physical connectivity (power, network cables)
2. Ping the IP: `ping 192.168.1.20`
3. Try from bastion: `ssh dev01` then `ssh ctr01`
4. Access via Proxmox console

**If accessible via Proxmox:**

```bash
# Check network interface
ip addr show eth0
systemctl status networking

# Check SSH
systemctl status sshd
journalctl -u sshd -n 50

# Check system load
top -bn1 | head -20
dmesg | tail -50
```

### High CPU/Memory Usage

**Symptoms:** System sluggish, services unresponsive.

**Diagnosis:**

```bash
# Top processes
top -bn1 | head -20

# Memory by process
ps aux --sort=-%mem | head -10

# Docker stats
docker stats --no-stream

# Check for runaway containers
docker ps --format "{{.Names}}" | xargs -I {} docker stats {} --no-stream
```

**Solutions:**

```bash
# Restart memory-hungry container
docker restart container-name

# Kill stuck process
kill -9 PID

# Clear system cache (safe)
sync; echo 3 > /proc/sys/vm/drop_caches
```

### VM Won't Start in Proxmox

**Symptoms:** VM stuck in "starting" or fails to boot.

**Diagnosis:**

1. Check Proxmox web UI for errors
2. Check VM console output
3. Review `/var/log/pve/tasks/` for task logs

**Common Causes:**

| Cause | Solution |
|-------|----------|
| GPU passthrough issue | Check IOMMU groups, reset GPU |
| Disk locked | Remove lock: `qm unlock VMID` |
| Resource contention | Check other VMs, reduce allocated resources |
| Cloud-init stuck | Access console, check `/var/log/cloud-init.log` |

---

## GPU Issues (RTX 2000E ADA)

### GPU Not Available in Container

**Symptoms:** NVIDIA GPU not visible in container.

**Diagnosis:**

```bash
# Check GPU on host
nvidia-smi

# Check container runtime
docker info | grep -i runtime

# Test GPU container
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**Solutions:**

```bash
# Restart NVIDIA services
sudo systemctl restart nvidia-persistenced

# Reload drivers
sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm

# Check container has GPU access
# In compose.yml:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### GPU Memory Exhausted

**Symptoms:** CUDA out of memory errors.

**Diagnosis:**

```bash
# Check GPU memory
nvidia-smi

# Find memory hogs
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
```

**Solutions:**

```bash
# Restart offending container
docker restart ollama

# Reduce model size or batch size in application config
```

---

## CI/CD Issues

### Pipeline Not Triggering

**Symptoms:** Push doesn't trigger GitLab CI.

**Diagnosis:**

1. Check `.gitlab-ci.yml` syntax
2. Verify pipeline is enabled in repo settings
3. Check runner availability

**Solutions:**

```bash
# Validate CI config locally
glab ci lint

# Check runner status
glab ci status
```

### Deploy Stage Failing

**Symptoms:** Pipeline passes validation but deploy fails.

**Diagnosis:**

```bash
# Check pipeline logs in GitLab UI
# Look for SSH or permission errors
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| SSH key not configured | Add deploy key to repo |
| Host unreachable from runner | Check firewall, runner network |
| docker compose syntax error | Test locally first |

---

## Emergency Procedures

### Complete Service Outage

1. **Triage:** Identify scope (single service vs host vs network)
2. **Check Traefik:** Is reverse proxy running?
3. **Check DNS:** Can you resolve names?
4. **Check Host:** Is ctr01 reachable?
5. **Check NFS:** Is storage mounted?

### Data Recovery

```bash
# List available backups
ls -la /mnt/synology/backups/

# Restore specific service data
rsync -av /mnt/synology/backups/service/latest/ /mnt/synology/docker/service/
```

### Nuclear Option: Rebuild Stack

```bash
# Stop everything
cd /opt/stacks/stack-name
docker compose down -v  # Warning: removes volumes

# Pull fresh
git fetch origin
git reset --hard origin/main

# Restore data from backup
# ...

# Start fresh
docker compose up -d
```

---

## Getting Help

If these runbooks don't solve your issue:

1. Check service-specific documentation
2. Search GitHub/GitLab issues
3. Check Discord communities (selfhosted, homelab)
4. Check Reddit r/selfhosted, r/homelab
5. Open an issue in the appropriate repository

---

## Related Documentation

- [Adding New Stacks](new-stack.md)
- [Service Catalog](../services/index.md)
- [ctr01 Stacks](../stacks/ctr01.md)
- [Network Topology](../architecture/network.md)
