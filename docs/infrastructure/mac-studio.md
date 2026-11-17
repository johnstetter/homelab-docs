# Mac Studio

The Studio is the homelab's AI server and John's desk machine. It's configured by the per-host layer of [mac-config](https://gitlab.com/stetter-homelab/mac-config): `setup/hosts/studio/` (its Brewfile, LaunchDaemon plists, pf rules and `setup.sh`).

| Property | Value |
|----------|-------|
| **Hardware** | Apple M5 Max, 64 GB, 1 TB internal + 2 TB external SSD |
| **Address** | `studio.rsdn.io` 192.168.1.95, tailnet `studio-ts` |
| **OS** | macOS 27 |
| **Docker** | OrbStack (per-user; only the Hermes sandbox uses it) |

## Unattended by Design

FileVault and auto-login are **off** on purpose, so after a reboot nobody is logged in and per-user LaunchAgents (`brew services`) never start. Every always-on service is therefore a **system LaunchDaemon** in `/Library/LaunchDaemons`, installed from the repo by `setup.sh`. Reboots on 2026-10-23 and 2026-10-28 came back clean with no console login.

What still needs a login: OrbStack (so Hermes' sandbox shell commands), Tailscale's GUI app, and the Keychain (glab, git signing).

## Daemons

| Label | Runs as | Port | Purpose |
|-------|---------|------|---------|
| `com.ollama.serve` | stetter | 11434 | Ollama from the `ollama-app` cask |
| `io.stetter.gpu-wired-limit` | root | - | Sets `iogpu.wired_limit_mb` to 7/8 of RAM at boot |
| `org.openwebui.server` | `_openwebui` | 8080 | Open WebUI |
| `org.openwebui.pf` | root | - | pf anchor: only Traefik + loopback reach :8080 |
| `com.hermes.dashboard` | stetter | 9119 | Hermes backend and web UI |
| `org.hermes.pf` | root | - | pf anchor: only Traefik + loopback reach :9119 |
| `com.hermes.gateway` | stetter | - | Hermes Discord/Telegram gateway |
| `io.stetter.node-exporter` | nobody | 9100 | node_exporter |
| `io.stetter.macmon` | nobody | 9101 | GPU/CPU/ANE power, temperatures, utilization |
| `io.stetter.gpu-metrics` | nobody | - | GPU unified memory + Ollama gauges (textfile) |
| `io.stetter.alloy` | nobody | - | Ships `ollama.log` to Loki on ctr01 |
| `io.stetter.log-rotate` | root | - | Copy-and-truncate rotation of `/var/log` daemon logs, 03:30 |
| `io.stetter.brew-maintenance` | stetter | - | `brew upgrade` daily at 04:00 |

## Storage

- Ollama models, OrbStack data and `/nix` stay on the **internal** disk. The external `studio-ssd` holds only Parallels VMs and games; core infrastructure must never depend on it.
- `/nas` is an autofs NFS mount of `syn:/volume1/media`, **read-only**, mounted on first access so it works with nobody logged in.

## Operations

```bash
# apply repo changes (only changed daemons restart)
sudo setup/hosts/studio/setup.sh
sudo setup/hosts/studio/setup.sh --reload        # restart all

# Ollama
curl -s 192.168.1.95:11434/api/version
ollama ps                                         # should show one model, 100% GPU, RUNNER mlx
setup/hosts/studio/ollama-upgrade.sh              # as stetter, not sudo; unloads models

# Open WebUI
sudo setup/hosts/studio/open-webui-upgrade.sh <version>
curl -s 127.0.0.1:8080/health                     # use loopback; the LAN address is filtered

# Hermes
hermes gateway status
cat ~/.hermes/gateway_state.json                  # telegram/discord "connected"

# daemon status
sudo launchctl list | grep -E 'ollama|hermes|openwebui|stetter'
```

Logs are in `/var/log/` (`ollama.log`, `open-webui.log`, `hermes-gateway.log`, `alloy.log`, ...).

## Gotchas

- **Never open Ollama.app.** Its menu-bar launcher starts a second server on :11434. The daemon runs the app's binary directly, and `setup.sh` refuses to run while the app is open.
- **`brew upgrade` skips `ollama-app`.** Use `ollama-upgrade.sh`, which also clears Gatekeeper's quarantine flag (otherwise the daemon hangs on a dialog nobody can answer).
- **Restarting Ollama unloads the model.** Hermes' next request then pays a 20-50 s cold prefill.
- **Wi-Fi stays on** alongside Ethernet: turning it off breaks Apple Watch unlock.
- **SSH password login is left enabled** on purpose.

## Related

- [Local AI](../architecture/ai.md)
- [Ollama](../services/ollama.md), [Open WebUI](../services/open-webui.md), [Hermes](../services/hermes.md)
