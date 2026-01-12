# Semaphore

Semaphore is a modern web UI for Ansible that provides a clean interface for running playbooks, managing inventories, and tracking task history.

## Access

| Property | Value |
|----------|-------|
| **URL** | [semaphore.rsdn.io](https://semaphore.rsdn.io) |
| **Stack** | [compose-stacks/management](https://gitlab.com/stetter-homelab/compose-stacks/management) |
| **Port** | 3000 |
| **Image** | `semaphoreui/semaphore:latest` |

## Authentication

Semaphore uses local authentication with username/password. Admin account is created during initial setup.

**Default admin:** Configured in docker-compose environment variables or during first-run setup.

---

## Common Operations

### Run a Playbook

1. Navigate to your project
2. Go to **Task Templates**
3. Click the **Run** button (play icon) on the template
4. Optionally set extra variables or limit hosts
5. Click **Run**
6. Monitor progress in the task output view

### View Task History

1. Navigate to your project
2. Go to **Task History** in the sidebar
3. View all previous runs with status (success/failed)
4. Click on a task to see full output and details

### Create a New Task Template

1. Go to **Task Templates > New Template**
2. Configure:
   - **Name**: Descriptive name for the task
   - **Playbook**: Select from repository files
   - **Inventory**: Choose target hosts
   - **Environment**: Select environment variables
   - **Repository**: Source repository containing playbooks
3. Save template

### Schedule Tasks

Set up recurring playbook runs:

1. Open a Task Template
2. Go to **Schedule** tab
3. Click **New Schedule**
4. Configure cron expression or interval
5. Save schedule

---

## Setting Up Projects

### Create a New Project

1. Click **New Project** on the dashboard
2. Enter project name and description
3. Save project

### Add a Repository

Connect to your GitLab repos containing Ansible playbooks:

1. Go to **Key Store** and add SSH key for GitLab access
2. Go to **Repositories > New Repository**
3. Configure:
   - **Name**: Repository identifier
   - **URL**: `git@gitlab.com:stetter-homelab/vm-platform.git`
   - **Branch**: `main`
   - **SSH Key**: Select key from Key Store
4. Save and wait for initial clone

### Configure Inventory

Define target hosts:

1. Go to **Inventory > New Inventory**
2. Choose inventory type:
   - **Static**: Define hosts in YAML format
   - **File**: Point to inventory file in repository
3. Configure:
   - **Name**: Inventory identifier
   - **SSH Key**: For connecting to hosts
   - **Inventory content or path**: Define hosts

**Static inventory example:**
```yaml
all:
  hosts:
    ctr01:
      ansible_host: 192.168.1.20
    dev01:
      ansible_host: 192.168.1.21
  vars:
    ansible_user: stetter
```

### Set Up Environment

Define environment variables for playbook runs:

1. Go to **Environment > New Environment**
2. Enter environment variables in JSON format:
```json
{
  "ANSIBLE_HOST_KEY_CHECKING": "False"
}
```
3. Save environment

---

## Integration with GitLab

### SSH Key Setup

1. Generate or use existing SSH key
2. Add public key to GitLab: User Settings > SSH Keys
3. In Semaphore: Key Store > New Key
   - Type: SSH Key
   - Paste private key content

### Webhook Integration (Optional)

Trigger Semaphore tasks from GitLab CI/CD:

1. In Semaphore, get the task webhook URL from template settings
2. In GitLab CI/CD, add job to trigger webhook:
```yaml
deploy:
  script:
    - 'curl -X POST "https://semaphore.rsdn.io/api/project/1/tasks" -H "Authorization: Bearer $SEMAPHORE_TOKEN"'
```

---

## Configuration

### Data Location

| Path | Location |
|------|----------|
| Config/Database | `/mnt/synology/docker/management/semaphore/data` |
| Repository Cache | `/mnt/synology/docker/management/semaphore/repositories` |

### Environment Variables

Key configuration in docker-compose:

| Variable | Description |
|----------|-------------|
| `SEMAPHORE_DB_DIALECT` | Database type (bolt, mysql, postgres) |
| `SEMAPHORE_ADMIN_*` | Initial admin credentials |
| `SEMAPHORE_ACCESS_KEY_ENCRYPTION` | Encryption key for stored credentials |

---

## Troubleshooting

### Repository Clone Failed

**Symptoms:** Repository shows error status, can't select playbooks

**Solutions:**

1. **Check SSH key permissions**
   ```bash
   # Verify key is added to GitLab
   ssh -T git@gitlab.com
   ```

2. **Test from container**
   ```bash
   ssh ctr01 'docker exec semaphore ssh -T git@gitlab.com'
   ```

3. **Re-add repository**
   - Delete and recreate repository in Semaphore
   - Ensure correct SSH key is selected

### Task Stuck or Hanging

```bash
# Check Semaphore logs
ssh ctr01 'docker logs semaphore --tail 100'

# Check for zombie processes
ssh ctr01 'docker exec semaphore ps aux'

# Restart container
ssh ctr01 'cd /opt/stacks/management && docker compose restart semaphore'
```

### Permission Denied on Target Hosts

1. **Verify SSH key in Key Store**
   - Key Store > Edit key > Ensure correct private key

2. **Check inventory SSH key assignment**
   - Inventory > Edit > Verify SSH key selected

3. **Test connectivity manually**
   ```bash
   ssh ctr01 'docker exec semaphore ssh -i /path/to/key user@target-host'
   ```

### Playbook Not Found

1. **Refresh repository**
   - Repositories > Click refresh icon
   - Wait for clone to complete

2. **Verify playbook path**
   - Path must be relative to repository root
   - Check branch is correct

### Database Locked (BoltDB)

If using BoltDB and experiencing lock issues:

```bash
# Stop container
ssh ctr01 'cd /opt/stacks/management && docker compose stop semaphore'

# Check for lock
ssh ctr01 'ls -la /mnt/synology/docker/management/semaphore/data/'

# Start container
ssh ctr01 'cd /opt/stacks/management && docker compose start semaphore'
```

### Container Not Starting

```bash
# Check container status
ssh ctr01 'docker ps -a | grep semaphore'

# View logs
ssh ctr01 'docker logs semaphore'

# Common issues:
# - Database permissions
# - Missing environment variables
# - Port conflict
```

---

## Best Practices

### Organizing Templates

- **Group by purpose**: deployment, maintenance, troubleshooting
- **Use descriptive names**: `Deploy - ctr01 Docker Stacks`
- **Add descriptions**: Document what the template does

### Security

- **Limit admin accounts**: Create user accounts with appropriate permissions
- **Rotate SSH keys**: Update keys periodically
- **Use project-level access**: Assign users to specific projects

### Task Management

- **Use task limits**: Limit concurrent tasks to prevent resource exhaustion
- **Review history**: Check failed tasks for patterns
- **Clean old tasks**: Periodically clean task history to save space

---

## Backup & Recovery

### Backup

Semaphore data is backed up via Synology Hyper Backup.

**Manual backup:**
```bash
# Backup data directory
ssh ctr01 'tar -czf /tmp/semaphore-backup.tar.gz -C /mnt/synology/docker/management/semaphore .'
scp ctr01:/tmp/semaphore-backup.tar.gz ./
```

### Recovery

1. Stop Semaphore: `docker compose stop semaphore`
2. Restore data to `/mnt/synology/docker/management/semaphore`
3. Start Semaphore: `docker compose start semaphore`

---

## Related

- [VM Lifecycle Runbook](../runbooks/vm-lifecycle.md) - Ansible deployment workflows
- [Management Stack](../stacks/ctr01.md#management)
- [vm-platform Repository](https://gitlab.com/stetter-homelab/vm-platform)
- [Semaphore Documentation](https://docs.semaphoreui.com/)
- [Ansible Documentation](https://docs.ansible.com/)
