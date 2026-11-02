# Hermes Agent

Self-hosted AI agent ([Nous Research Hermes Agent](https://hermes-agent.nousresearch.com)) running on the Mac Studio's local model. It reports on and does light work across the homelab, while Claude Code does the heavy lifting.

| Property | Value |
|----------|-------|
| **Dashboard** | [hermes.rsdn.io](https://hermes.rsdn.io) |
| **Host** | Mac Studio, installed by Hermes' own installer under `~/.hermes` |
| **Version** | v0.22.5 |
| **Model** | `qwen3.8:27b-mxfp8-64k` (64k context); fallbacks in [Local AI](../architecture/ai.md#ollama) |
| **Chat channels** | Web dashboard, desktop app (Air, over SSH), Discord, Telegram |
| **Config** | `~/.hermes/config.yaml`, `SOUL.md` (private git repo); daemon plists in mac-config |

## Components

| Component | Daemon | Notes |
|-----------|--------|-------|
| Backend + web dashboard | `com.hermes.dashboard` | `hermes dashboard --host 0.0.0.0 --port 9119`. Basic auth, TLS from Traefik, pf limits :9119 to Traefik and loopback |
| Messaging gateway | `com.hermes.gateway` | Discord and Telegram bots; waits for DNS at boot before connecting |
| Sandbox | `hermes-*` OrbStack container | Where agent shell commands run. Has its own SSH key, GitLab token and Grafana token; never sees `~/.hermes` |

Only one backend per host: a second `hermes dashboard` or `hermes serve` makes the first one reap it.

## Access Model

Hermes gets its own identities, and they're narrow:

| Target | Identity | Can | Can't |
|--------|----------|-----|-------|
| ctr01, dev01, sec01, nexus, pve-tc1 | Unix user `hermes` (UID 1100), key bound to the Studio's IP | Read `/var/log` and the journal; `hermes-docker` (ctr01) ps/stats/logs/start/stop/restart/compose-up; `hermes-pve` list/status/start/shutdown/reboot guests | General sudo, the docker group, NFS mounts |
| GitLab (`stetter-homelab` group) | Service account, Developer | Branches, MRs, pipelines | Push or merge to protected `main` |
| Grafana | Viewer service account | Query Loki and Prometheus through the data-source proxy | Write to Loki, Prometheus admin API |
| Home Assistant | HA's MCP server | Assist tools on exposed entities | HA configuration |
| Google Workspace | OAuth, six `*.readonly` scopes | Read mail, calendar, drive | Send, draft, edit |

The sudo wrappers live in vm-platform (`ansible/files/hermes/`, playbook `hermes-user.yml`). To give Hermes a new ability, add a verb to a wrapper; don't widen sudoers. The Synology has no `hermes` account (DSM only allows SSH for admins).

Repos mounted read-write into the sandbox: `compose-stacks` and `vm-platform`. `mac-config` isn't mounted, because `setup.sh` runs from it as root.

## Operations

```bash
hermes gateway status
hermes mcp test home-assistant
cat ~/.hermes/gateway_state.json                         # platforms "connected"
sudo launchctl kickstart -k system/com.hermes.dashboard   # restart after config changes
sudo launchctl kickstart -k system/com.hermes.gateway
docker rm -f $(docker ps -qf name=hermes-)                # after changing forwarded env or mounts
```

After a reboot, sandbox commands fail until someone logs in at the console and OrbStack starts. After `hermes update`, macOS may ask again for Local Network permission, which Hermes' Python needs to reach Home Assistant.

## Revoking

Remove the GitLab service account from the group, delete the Grafana service account, delete the HA token, and on each host `userdel -r hermes` plus `/etc/sudoers.d/hermes`.
