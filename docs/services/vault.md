# Vault

HashiCorp Vault for secrets management in the homelab.

## Access

| Property | Value |
|----------|-------|
| **URL** | [vault.rsdn.io](https://vault.rsdn.io) |
| **Stack** | [compose-stacks/core](https://gitlab.com/stetter-homelab/compose-stacks/core) |
| **Port** | 8200 |
| **Image** | `hashicorp/vault:1.21` |

## Authentication

Vault uses token-based authentication. The root token is generated during initialization.

**Token location:** Stored securely (not in git). Check 1Password or your secrets manager.

## Status Check

```bash
# Check if Vault is sealed/unsealed
ssh ctr01 'docker exec vault vault status'
```

**Status indicators:**
- `Sealed: false` - Vault is operational
- `Sealed: true` - Vault needs to be unsealed

---

## Common Operations

### Unseal Vault

After a restart, Vault starts in a sealed state and must be unsealed with unseal keys.

```bash
# SSH to ctr01
ssh ctr01

# Check current status
docker exec vault vault status

# Unseal (requires 3 of 5 keys by default)
docker exec -it vault vault operator unseal
# Enter unseal key 1

docker exec -it vault vault operator unseal
# Enter unseal key 2

docker exec -it vault vault operator unseal
# Enter unseal key 3

# Verify unsealed
docker exec vault vault status
```

!!! warning "Unseal Keys"
    Store unseal keys securely and separately. Never store all keys in the same location.

### Login via CLI

```bash
# Login with root token
docker exec -it vault vault login

# Login with specific token
docker exec vault vault login <token>
```

### Read a Secret

```bash
# KV v2 secrets engine (default path: secret/)
docker exec vault vault kv get secret/my-app/config

# Get specific field
docker exec vault vault kv get -field=password secret/my-app/config
```

### Write a Secret

```bash
# Write key-value pairs
docker exec vault vault kv put secret/my-app/config \
  username="myuser" \
  password="mypassword"

# Write from file
docker exec vault vault kv put secret/my-app/config @data.json
```

### List Secrets

```bash
# List paths at a location
docker exec vault vault kv list secret/

# List all secret engines
docker exec vault vault secrets list
```

### Delete a Secret

```bash
# Soft delete (can be recovered)
docker exec vault vault kv delete secret/my-app/config

# Permanent delete (destroy all versions)
docker exec vault vault kv destroy -all-versions secret/my-app/config
```

---

## Web UI

Access the Vault UI at [vault.rsdn.io](https://vault.rsdn.io).

**Login methods:**
- **Token** - Use root token or generated token
- **Userpass** - If userpass auth method is enabled

**Common UI tasks:**
1. Browse secrets under "Secrets Engines"
2. Create new secrets with the "+ Create secret" button
3. View/rotate secrets by clicking on paths

---

## Configuration

### Storage Backend

Vault uses file-based storage at `/vault/file` (NFS mount to Synology).

**Config location:** `compose-stacks/core/config/vault/config.hcl`

```hcl
storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true  # TLS handled by Traefik
}

ui = true
```

### Data Location

| Path | Location |
|------|----------|
| Vault data | `/mnt/synology/docker/core/vault/file` |
| Vault logs | `/mnt/synology/docker/core/vault/logs` |

---

## Backup & Recovery

### Backup

Vault data is backed up automatically via Synology Hyper Backup.

**Manual snapshot:**
```bash
# Create Raft snapshot (if using Raft storage)
docker exec vault vault operator raft snapshot save /vault/logs/backup.snap

# Copy to local machine
scp ctr01:/mnt/synology/docker/core/vault/logs/backup.snap ./
```

### Recovery

1. Stop Vault: `docker compose stop vault`
2. Restore data to `/mnt/synology/docker/core/vault/file`
3. Start Vault: `docker compose start vault`
4. Unseal with original unseal keys

---

## Troubleshooting

### Vault is Sealed After Restart

This is expected behavior. Unseal using the procedure above.

**Auto-unseal options:**
- Transit auto-unseal (requires another Vault)
- Cloud KMS (AWS, GCP, Azure)
- Not recommended for homelab due to complexity

### Permission Denied

```bash
# Check token permissions
docker exec vault vault token capabilities secret/my-app/config

# List current token info
docker exec vault vault token lookup
```

### Can't Access Web UI

1. Check container is running: `docker ps | grep vault`
2. Check Traefik routing: Visit [traefik.rsdn.io](https://traefik.rsdn.io)
3. Check logs: `docker logs vault`

### Lost Root Token

If you've lost the root token but have unseal keys:

```bash
# Generate new root token
docker exec -it vault vault operator generate-root -init
# Follow the prompts with unseal keys
```

---

## Integration Examples

### Docker Compose with Vault

```yaml
services:
  myapp:
    environment:
      - DB_PASSWORD=${DB_PASSWORD}  # From .env, sourced from Vault
```

### Fetching Secrets in Scripts

```bash
#!/bin/bash
# Requires VAULT_ADDR and VAULT_TOKEN environment variables

export VAULT_ADDR="https://vault.rsdn.io"
export VAULT_TOKEN="your-token"

# Get secret
DB_PASS=$(vault kv get -field=password secret/myapp/db)
```

---

## Related

- [Core Stack](../stacks/ctr01.md#core)
- [Vault Official Docs](https://developer.hashicorp.com/vault/docs)
- [Troubleshooting Runbook](../runbooks/troubleshooting.md)
