# SearXNG

Metasearch engine used as Open WebUI's web search backend.

| Property | Value |
|----------|-------|
| **URL** | [search.rsdn.io](https://search.rsdn.io) |
| **Host** | ctr01, [ai stack](../stacks/ctr01.md#ai) |
| **Direct port** | `ctr01:8081` |
| **Egress** | ProtonVPN WireGuard via `gluetun-searxng` |

## Design

- `searxng` uses `network_mode: service:gluetun-searxng`, so every upstream query leaves through the VPN. The home IP was being CAPTCHA'd or 403'd by DuckDuckGo, Google, Brave and Startpage. The Traefik labels and port mapping sit on the gluetun container, since it owns the network namespace.
- The tunnel has its own Proton key, separate from the media stack's gluetun.
- `settings.yml` in the repo is a template: an entrypoint wrapper substitutes the Brave API key from the environment at start, because SearXNG can't read engine keys from env vars.

| Engine | State |
|--------|-------|
| braveapi | On (official API, free tier ~1 req/s with a monthly cap) |
| bing, mojeek, wikipedia | On |
| brave (scraped), duckduckgo | Off: 429/403 |
| google, startpage | Off, untested through the VPN |

## Checks

```bash
docker exec gluetun-searxng wget -qO- https://api.ipify.org     # a Proton IP, not home
curl -s 'http://ctr01:8081/search?q=test&format=json' | jq '.unresponsive_engines'
docker logs searxng --since 1h 2>&1 | grep 'ERROR:searx.engines'
```

Daily query volume:

```promql
sum(increase(traefik_service_requests_total{service="searxng@docker"}[1d]))
```
