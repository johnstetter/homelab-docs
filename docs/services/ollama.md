# Ollama

Two Ollama instances, each with a single resident model. The why is in [Local AI](../architecture/ai.md).

| | Mac Studio | ctr01 |
|---|---|---|
| **Endpoint** | `http://studio.rsdn.io:11434` | `http://ctr01.rsdn.io:11434` |
| **Install** | `ollama-app` cask, system LaunchDaemon `com.ollama.serve` | `ollama/ollama` container, [ai stack](../stacks/ctr01.md#ai) |
| **Version** | 0.40.12 | 0.40.13 (Renovate-pinned) |
| **Accelerator** | M5 Max GPU, MLX engine, 56 GiB wired limit | RTX 2000E Ada 16 GB, CUDA |
| **Resident model** | `qwen3.8:27b-mxfp8-64k` | `gpt-oss-ha:20b` |
| **Clients** | Hermes, Open WebUI | Home Assistant |
| **Config repo** | mac-config `setup/hosts/studio/` | compose-stacks/ai |
| **Auth** | None (LAN) | None (LAN) |

Neither instance is behind Traefik; both are plain HTTP on the LAN with no authentication.

## Studio

Environment set in `com.ollama.serve.plist`:

| Variable | Value | Why |
|----------|-------|-----|
| `OLLAMA_HOST` | `0.0.0.0` | Remote clients |
| `OLLAMA_KEEP_ALIVE` | `-1` | The model never unloads, so no reload stalls |
| `OLLAMA_CONTEXT_LENGTH` | `16384` | Default for small models; the `-64k` tags set their own 65536 |

`OLLAMA_NUM_PARALLEL` stays at 1: tested at 2, the MLX runner still ran requests one after another.

Models: see the table in [Local AI](../architecture/ai.md#ollama). Each `-64k` model is a one-line Modelfile over the stock tag (`PARAMETER num_ctx 65536`); reference copies are in `setup/hosts/studio/ollama/`.

```bash
ollama list
ollama ps                                   # RUNNER mlx, 100% GPU, UNTIL Forever
ollama stop <model>                          # before loading a different large model
setup/hosts/studio/ollama-upgrade.sh         # upgrade (as stetter)
grep -E 'evict|Structured output' /var/log/ollama.log | tail
```

!!! warning "One large model at a time"
    The 8-bit 27B uses up to ~44 GB with a full prompt cache. Loading any other large model evicts it, and Hermes pays a cold prefill on its next request.

## ctr01

Environment from `compose.yml`:

| Variable | Value |
|----------|-------|
| `OLLAMA_KEEP_ALIVE` | `-1` |
| `OLLAMA_MAX_LOADED_MODELS` | `1` |
| `OLLAMA_NUM_PARALLEL` | `1` |
| `OLLAMA_CONTEXT_LENGTH` | `16384` (must match HA's context setting, or Ollama reloads) |
| `OLLAMA_FLASH_ATTENTION` | `1` |

`gpt-oss-ha:20b` is built from `ollama/gpt-oss-ha.Modelfile` in the ai stack: same weights as `gpt-oss:20b`, low reasoning by default. In Home Assistant: model `gpt-oss-ha:20b`, Think before responding **off**, context 16384, keep alive -1.

```bash
docker exec ollama ollama ps                # 100% GPU; a CPU/GPU split means it doesn't fit
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
docker logs ollama --since 10m | grep POST   # per-request latency, client 192.168.1.3 is HA
```

## Metrics

Both instances publish the same gauges through node-exporter's textfile collector (`ollama_up`, `ollama_loaded_models`, `ollama_model_vram_bytes`, `ollama_model_context_length`, ...); only the `job` label differs. Request latency comes from Ollama's own log in Loki. Dashboards: **Mac Studio** and **ctr01 — AI Load** in Grafana.
