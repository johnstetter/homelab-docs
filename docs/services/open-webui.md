# Open WebUI

Chat UI for the Studio's local models.

| Property | Value |
|----------|-------|
| **URL** | [chat.rsdn.io](https://chat.rsdn.io) (also `ai.rsdn.io`) |
| **Host** | Mac Studio, native install, LaunchDaemon `org.openwebui.server` |
| **Version** | 0.12.4 (pinned as `OW_VERSION` in `setup.sh`) |
| **Account** | `_openwebui` (UID 450, hidden, non-admin) |
| **Data** | `/var/openwebui/data` (internal disk) |
| **Backend** | Ollama on the Studio, `qwen3.8:27b-mxfp8-64k` (shared with Hermes) |
| **Web search** | SearXNG, `https://search.rsdn.io` |
| **Config repo** | mac-config `setup/hosts/studio/` |

## How It's Wired

- Traefik on ctr01 routes `chat.rsdn.io` → `http://192.168.1.95:8080` (file provider in compose-stacks/core).
- The pf anchor `com.apple/openwebui` drops every connection to :8080 except from ctr01 and loopback. `http://studio:8080` from another machine is supposed to fail.
- Open WebUI's Tools and Functions run arbitrary Python inside the server, so it runs under its own role account. A deny ACL on `/Users/stetter` keeps that account out of John's files, and `setup.sh` refuses to continue if the account can read them or is an admin.
- Secrets (`WEBUI_SECRET_KEY`, first-run admin) live in `/usr/local/etc/open-webui/env` (mode 600), sourced from 1Password, never in the repo.
- `ENABLE_SIGNUP=false`. Settings changed in the admin UI persist in the database and override the plist.

## Web Search

Admin Settings → Web Search points at SearXNG on ctr01 with **1 concurrent request and 3 results**, so one question doesn't burn through the Brave Search API free tier. See the [ai stack](../stacks/ctr01.md#ai).

## Operations

```bash
curl -s 127.0.0.1:8080/health                                   # on the Studio
sudo setup/hosts/studio/open-webui-upgrade.sh <new-version>     # backup, reinstall, health check, auto-rollback
tail -f /var/log/open-webui.log
```

After an upgrade, check Admin Settings for stale values (persisted settings win over the plist), and delete `/var/openwebui/data.bak-<old>` once the new version has survived a few reboots.

## History

Ran as a container in ctr01's ai stack until 2026-10-09, when its data moved to the Studio. The ctr01 container is gone.
