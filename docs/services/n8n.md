# n8n

Workflow automation platform for connecting services and automating tasks.

## Access

| Property | Value |
|----------|-------|
| **URL** | [n8n.rsdn.io](https://n8n.rsdn.io) |
| **Stack** | [compose-stacks/ai](https://gitlab.com/stetter-homelab/compose-stacks/ai) |
| **Port** | 5678 |
| **Image** | `n8nio/n8n:2.1.4` |

## Authentication

n8n uses basic authentication configured in the stack `.env`:

- Username: `N8N_BASIC_AUTH_USER`
- Password: `N8N_BASIC_AUTH_PASSWORD`

---

## Common Operations

### View Workflows

1. Go to [n8n.rsdn.io](https://n8n.rsdn.io)
2. Log in with your credentials
3. Click **Workflows** in the sidebar

### Create a Workflow

1. Click **Add Workflow** or press `Ctrl+Alt+N`
2. Click the **+** button to add nodes
3. Connect nodes by dragging from output to input
4. Configure each node with required parameters
5. Click **Save** to save the workflow
6. Toggle **Active** to enable scheduled or webhook triggers

### Execute a Workflow Manually

1. Open the workflow
2. Click **Execute Workflow** button (or press `Ctrl+Enter`)
3. View execution results in the right panel

### View Execution History

1. Open a workflow
2. Click **Executions** tab at the top
3. View past runs with status (success/failed)
4. Click any execution to see detailed node-by-node results

### Manage Credentials

1. Go to **Settings** (gear icon) in the sidebar
2. Click **Credentials**
3. Click **Add Credential** to create new
4. Select the service type (HTTP, OAuth, API key, etc.)
5. Enter the required authentication details
6. Save and test the connection

---

## Webhook Integration

### Create a Webhook Endpoint

1. Add a **Webhook** node as your workflow trigger
2. Choose HTTP method (GET, POST, etc.)
3. Copy the webhook URL (format: `https://n8n.rsdn.io/webhook/<path>`)
4. Configure response options if needed
5. Save and activate the workflow

**Webhook URL format:**
```
Production: https://n8n.rsdn.io/webhook/<webhook-path>
Test:       https://n8n.rsdn.io/webhook-test/<webhook-path>
```

### Test Webhooks

1. Open the workflow in edit mode
2. Click **Execute Workflow**
3. Send a request to the test webhook URL
4. View incoming data in the Webhook node output

!!! note "Test vs Production URLs"
    Test webhooks only work while the workflow is open in the editor.
    Production webhooks work when the workflow is active.

---

## Common Workflow Examples

### API to API Integration

```
Webhook → HTTP Request → Set → HTTP Request → Respond
```

Connect external triggers to internal services (e.g., receive GitHub webhook, update a database, notify via Slack).

### Scheduled Data Sync

```
Cron → HTTP Request → Loop Over Items → Database Insert
```

Pull data from an API on a schedule and sync to a database.

### Error Alerting

```
Error Trigger → Slack/Discord/Email
```

Get notified when any workflow fails.

### Home Assistant Automation

```
Webhook (from HA) → Switch → Multiple Actions
```

Receive Home Assistant events and trigger complex multi-service actions.

---

## Configuration

### Database

n8n uses PostgreSQL for persistent storage:

| Setting | Value |
|---------|-------|
| **Database Host** | `postgres-n8n` (internal container) |
| **Database Port** | 5432 (internal) / 5433 (host mapped) |
| **Database Name** | Configured via `N8N_POSTGRES_DB` |

### Data Location

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/ai/n8n` | n8n configuration and workflow data |
| `ai_postgres_n8n` volume | PostgreSQL database data |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `N8N_HOST` | External hostname |
| `N8N_BASIC_AUTH_USER` | Admin username |
| `N8N_BASIC_AUTH_PASSWORD` | Admin password |
| `N8N_POSTGRES_DB` | Database name |
| `N8N_POSTGRES_USER` | Database user |
| `N8N_POSTGRES_PASSWORD` | Database password |
| `N8N_WEBHOOK_URL` | External webhook base URL |
| `N8N_TIMEZONE` | Timezone for scheduling |

---

## Troubleshooting

### Workflow Execution Failed

1. **Check execution log:**
   - Open the workflow
   - Go to **Executions** tab
   - Click the failed execution
   - Review error message on the failing node

2. **Common causes:**
   - Invalid credentials (expired token, wrong API key)
   - Network issues (service unreachable)
   - Rate limiting (too many requests)
   - Invalid data format (unexpected response structure)

3. **Debug with test execution:**
   - Open workflow editor
   - Click failing node
   - Run just that node with test data

### Webhook Not Receiving Data

1. **Verify workflow is active** (toggle switch is on)
2. **Check the URL:**
   - Use production URL (`/webhook/`) not test URL
   - Ensure path matches exactly
3. **Test with curl:**
   ```bash
   curl -X POST https://n8n.rsdn.io/webhook/your-path \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```
4. **Check Traefik logs** for routing issues

### Credentials Not Working

1. **Test credentials independently:**
   - Create a simple test workflow
   - Add an HTTP Request node
   - Test the API endpoint manually
2. **Check credential type** matches the service
3. **Verify OAuth tokens** haven't expired
4. **Check API key permissions** on the external service

### Workflow Runs Slowly

1. **Review loop nodes** - process items in batches
2. **Add delays** between API calls to avoid rate limits
3. **Use the SplitInBatches node** for large datasets
4. **Check external service response times**

### Database Connection Error

1. **Check PostgreSQL container:**
   ```bash
   ssh ctr01 'docker logs postgres-n8n'
   ```
2. **Verify container is running:**
   ```bash
   ssh ctr01 'docker ps | grep postgres-n8n'
   ```
3. **Restart if needed:**
   ```bash
   ssh ctr01 'cd /opt/stacks/ai && docker compose restart postgres-n8n n8n'
   ```

### Can't Access n8n UI

1. **Check container status:**
   ```bash
   ssh ctr01 'docker ps | grep n8n'
   ```
2. **Check Traefik routing:**
   - Verify n8n appears in [traefik.rsdn.io](https://traefik.rsdn.io)
3. **Check container logs:**
   ```bash
   ssh ctr01 'docker logs n8n --tail 100'
   ```

---

## Backup and Restore

### Backup Strategy

- **Workflow data:** Stored on NFS at `/mnt/synology/docker/ai/n8n`
- **Database:** PostgreSQL in `ai_postgres_n8n` volume

### Export Workflows

1. Go to **Settings** → **Workflows**
2. Select workflows to export
3. Click **Export**

Or use the API:
```bash
curl -u admin:password https://n8n.rsdn.io/api/v1/workflows \
  -o workflows-backup.json
```

### Import Workflows

1. Go to **Workflows** → **Import from file**
2. Select the JSON backup file
3. Review and save imported workflows

---

## Related

- [AI Stack](../stacks/ctr01.md#ai)
- [n8n Documentation](https://docs.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
