# Technitium

Technitium DNS Server for authoritative DNS and local resolution across the homelab.

## Access

| Property | Value |
|----------|-------|
| **Primary URL** | [technitium-syn.rsdn.io](https://technitium-syn.rsdn.io) |
| **Secondary URL** | [technitium-ctr.rsdn.io](https://technitium-ctr.rsdn.io) |
| **Stack** | [compose-stacks/technitium](https://gitlab.com/stetter-homelab/compose-stacks/technitium) |
| **Port** | 5380 (Web UI), 53 (DNS) |
| **Image** | `technitium/dns-server` |

## Architecture

The homelab runs two Technitium instances for redundancy:

| Instance | Host | IP | Role |
|----------|------|-----|------|
| Primary | Synology NAS | 192.168.1.4 | Main DNS, authoritative for rsdn.io |
| Secondary | ctr01 | 192.168.1.20 | Backup DNS, zone replica |

**DNS Flow:**
1. Clients query primary (192.168.1.4:53)
2. If unavailable, failover to secondary (192.168.1.20:53)
3. UDM Pro configured with both as DNS servers

---

## Common Operations

### Add a DNS Record

1. Log in to [technitium-syn.rsdn.io](https://technitium-syn.rsdn.io)
2. Navigate to **Zones** > **rsdn.io**
3. Click **Add Record**
4. Configure:
   - **Name:** `myservice` (for myservice.rsdn.io)
   - **Type:** A, CNAME, or other
   - **Value:** IP address or target hostname
   - **TTL:** 3600 (default)
5. Click **Add Record**

**Common record types:**
- **A Record:** `myservice` → `192.168.1.100`
- **CNAME:** `myservice` → `rprx.rsdn.io` (for Traefik-proxied services)

### Create a New Zone

```bash
# Via Web UI:
# 1. Navigate to Zones
# 2. Click "Add Zone"
# 3. Enter zone name (e.g., internal.rsdn.io)
# 4. Select zone type (Primary for authoritative)
```

### View Query Logs

1. Go to **Logs** in the web UI
2. Filter by:
   - Client IP
   - Query name
   - Response type (success, blocked, etc.)

**CLI query log check:**
```bash
# Check DNS logs on primary
ssh syn 'docker logs technitium-dns --tail 100'

# Check DNS logs on secondary
ssh ctr01 'docker logs technitium --tail 100'
```

### Test DNS Resolution

```bash
# Query primary DNS server
dig @192.168.1.4 myservice.rsdn.io

# Query secondary DNS server
dig @192.168.1.20 myservice.rsdn.io

# Check propagation
dig +short myservice.rsdn.io

# Trace resolution path
dig +trace myservice.rsdn.io
```

### Flush DNS Cache

```bash
# Via Web UI: Settings > Cache > Clear Cache

# Or via API
curl -X POST "http://192.168.1.4:5380/api/cache/clear?token=YOUR_TOKEN"
```

### Zone Transfer (Primary to Secondary)

Zone transfers happen automatically, but you can force sync:

1. On secondary, go to **Zones** > **rsdn.io**
2. Click **Refresh** to pull latest from primary

---

## Configuration

### Zone Configuration

| Zone | Type | Purpose |
|------|------|---------|
| `rsdn.io` | Primary | Main homelab domain |
| `1.168.192.in-addr.arpa` | Primary | Reverse DNS for 192.168.1.0/24 |
| `10.0.10.in-addr.arpa` | Primary | Reverse DNS for storage network |

### Key Settings

**Forwarders (for external resolution):**
- Cloudflare: `1.1.1.1`, `1.0.0.1`
- Quad9: `9.9.9.9`

**Recursion:** Enabled for local clients only (192.168.0.0/16, 10.0.0.0/8)

**DNSSEC:** Optional, configure per-zone

### Data Location

| Path | Location |
|------|----------|
| Primary config | `/volume1/docker/technitium/config` (Synology) |
| Secondary config | `/mnt/synology/docker/technitium/config` (ctr01) |
| Zones | Stored within config directory |

---

## DNS Blocking

Technitium supports ad/tracker blocking via block lists.

### Add Block List

1. Go to **Settings** > **Blocking**
2. Under "Block List URLs", add:
   ```
   https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
   ```
3. Click **Save Settings**
4. Click **Update Block Lists Now**

### Whitelist a Domain

1. Go to **Settings** > **Blocking**
2. Add domain to **Custom Allow List**
3. Save and apply

---

## Troubleshooting

### DNS Resolution Failing

1. **Check server is running:**
   ```bash
   # Primary
   ssh syn 'docker ps | grep technitium'

   # Secondary
   ssh ctr01 'docker ps | grep technitium'
   ```

2. **Verify port 53 is accessible:**
   ```bash
   # Test TCP
   nc -zv 192.168.1.4 53

   # Test UDP
   nmap -sU -p 53 192.168.1.4
   ```

3. **Check Technitium logs:**
   ```bash
   ssh syn 'docker logs technitium-dns --tail 50'
   ```

### Zone Not Syncing to Secondary

1. Check zone transfer settings on primary
2. Verify secondary is configured as authorized transfer target
3. Check network connectivity between instances
4. Review logs for transfer errors

### Slow DNS Queries

1. Check forwarder health in Settings > Forwarders
2. Review cache hit rate in Dashboard
3. Consider adding more upstream resolvers
4. Check for DNS loops (query logs show excessive recursion)

### Web UI Not Accessible

```bash
# Check container is running
docker ps | grep technitium

# Verify port binding
ss -tlnp | grep 5380

# Check container logs
docker logs technitium --tail 50

# Restart if needed
docker restart technitium
```

### Records Not Resolving

1. Verify record exists in zone
2. Check TTL (cached records may not update immediately)
3. Flush local DNS cache: `sudo systemd-resolve --flush-caches`
4. Check for conflicting records (multiple A records, etc.)

---

## API Usage

Technitium provides a REST API for automation.

### Get API Token

1. Log in to web UI
2. Go to **Settings** > **API**
3. Create or copy API token

### Common API Calls

```bash
# Set token
TOKEN="your-api-token"
DNS="192.168.1.4:5380"

# List zones
curl "http://$DNS/api/zones/list?token=$TOKEN"

# Add A record
curl -X POST "http://$DNS/api/zones/records/add?token=$TOKEN" \
  -d "domain=myservice.rsdn.io" \
  -d "type=A" \
  -d "value=192.168.1.100" \
  -d "ttl=3600"

# Delete record
curl -X POST "http://$DNS/api/zones/records/delete?token=$TOKEN" \
  -d "domain=myservice.rsdn.io" \
  -d "type=A" \
  -d "value=192.168.1.100"

# Clear cache
curl -X POST "http://$DNS/api/cache/clear?token=$TOKEN"
```

---

## Related

- [Core Stack](../stacks/ctr01.md#core)
- [Traefik](traefik.md) - Reverse proxy (uses DNS for routing)
- [Technitium Official Docs](https://technitium.com/dns/)
- [Troubleshooting Runbook](../runbooks/troubleshooting.md)
