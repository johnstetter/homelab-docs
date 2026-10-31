# Authentik

Identity provider for the lab: forward auth in front of admin UIs and OIDC for apps that support it.

| Property | Value |
|----------|-------|
| **URL** | [sso.rsdn.io](https://sso.rsdn.io) |
| **Stack** | [compose-stacks/authentik](https://gitlab.com/stetter-homelab/compose-stacks/authentik) on ctr01 |
| **Version** | 2026.5 |
| **Containers** | `authentik` (server + embedded outpost), `authentik-worker`, `authentik-db` (Postgres 16), `authentik-redis` |

## What Uses It

| App | Method | Who gets in |
|-----|--------|-------------|
| Traefik dashboard | Forward auth (`authentik@docker`) | `Homelab Admins` |
| Grafana | OIDC | `Homelab Admins` |

`Homelab Admins` (members `stetter`, `akadmin`) isn't a superuser group: membership opens admin apps without making someone an Authentik admin.

## Config as Code

Providers, applications, groups and outpost assignments are **blueprints** in `blueprints/`, not UI clicks:

- `homelab-admins.yaml`: the group
- `traefik-dashboard.yaml`: forward-auth provider, application and outpost entry for the dashboard
- `grafana.yaml`: Grafana OAuth2 provider and application. `client_id`/`client_secret` are deliberately left out, so they keep their stored values (the same values are in the monitoring stack's `.env`)

!!! warning "Outpost provider list"
    The embedded outpost entry **replaces** the outpost's provider list. When adding a second forward-auth app, list every provider in one place, or the last blueprint applied drops the others.

## Protecting a New App

1. Add a forward-auth provider + application blueprint, bound to `Homelab Admins`.
2. Add the provider to the outpost's list.
3. Add `traefik.http.routers.<name>.middlewares=authentik@docker` to the app's router.

The `authentik-outpost` router already sends `/outpost.goauthentik.io/` on any `*.rsdn.io` host to the embedded outpost.

## Failure Mode

If Authentik is down, every router using the middleware returns an error. For the Traefik dashboard, fall back to `docker logs traefik` or start Authentik again.
