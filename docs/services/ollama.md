# Ollama

Ollama local LLM server for running language models on GPU hardware.

## Access

| Property | Value |
|----------|-------|
| **API** | `http://ctr01:11434` (internal only) |
| **Web UI** | [chat.rsdn.io](https://chat.rsdn.io) (Open-WebUI) |
| **Stack** | [compose-stacks/ai](https://gitlab.com/stetter-homelab/compose-stacks/ai) |
| **Port** | 11434 |
| **Image** | `ollama/ollama` |
| **GPU** | NVIDIA RTX2000E ADA 16GB |

## Architecture

Ollama runs on ctr01 with GPU passthrough:

- **Compute:** RTX2000E ADA with 16GB VRAM
- **Storage:** Models stored on NFS (`/mnt/synology/docker/ai/ollama/models`)
- **Frontend:** Open-WebUI provides ChatGPT-like interface at chat.rsdn.io

---

## Common Operations

### Pull a Model

```bash
# SSH to ctr01
ssh ctr01

# Pull a model
docker exec ollama ollama pull llama3.2

# Pull specific version
docker exec ollama ollama pull llama3.2:70b

# Popular models:
# - llama3.2 (8B, ~4GB)
# - llama3.2:70b (70B, ~40GB - won't fit in 16GB VRAM)
# - mistral (7B, ~4GB)
# - codellama (7B, ~4GB)
# - phi3 (3B, ~2GB)
```

### List Installed Models

```bash
# List all models
docker exec ollama ollama list

# Show model details
docker exec ollama ollama show llama3.2
```

### Remove a Model

```bash
# Remove a model
docker exec ollama ollama rm llama3.2:70b

# Check disk space after removal
df -h /mnt/synology/docker/ai/ollama
```

### Run Inference (CLI)

```bash
# Interactive chat
docker exec -it ollama ollama run llama3.2

# Single prompt
docker exec ollama ollama run llama3.2 "Explain kubernetes in one sentence"

# With specific parameters
docker exec -it ollama ollama run llama3.2 --num-ctx 4096
```

### Check GPU Memory

```bash
# View GPU utilization
ssh ctr01 'nvidia-smi'

# Watch GPU memory during inference
ssh ctr01 'watch -n 1 nvidia-smi'

# Check Ollama GPU usage
ssh ctr01 'nvidia-smi --query-compute-apps=pid,used_memory --format=csv'
```

---

## API Usage

Ollama exposes a REST API on port 11434.

### Generate Completion

```bash
# From ctr01 or any host on the network
curl http://ctr01:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

### Chat Completion (OpenAI-compatible)

```bash
curl http://ctr01:11434/v1/chat/completions -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ]
}'
```

### Streaming Response

```bash
curl http://ctr01:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Write a haiku about containers",
  "stream": true
}'
```

### List Models via API

```bash
curl http://ctr01:11434/api/tags
```

### Check Model Status

```bash
# Check if model is loaded in memory
curl http://ctr01:11434/api/ps
```

---

## Configuration

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `OLLAMA_MODELS` | Model storage path (default: `/root/.ollama/models`) |
| `OLLAMA_HOST` | Bind address (default: `0.0.0.0:11434`) |
| `OLLAMA_NUM_PARALLEL` | Concurrent requests (default: 1) |
| `OLLAMA_MAX_LOADED_MODELS` | Models in VRAM (default: 1) |

### Docker Compose Labels

```yaml
services:
  ollama:
    image: ollama/ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - /mnt/synology/docker/ai/ollama:/root/.ollama
    ports:
      - "11434:11434"
```

### Data Location

| Path | Location |
|------|----------|
| Models | `/mnt/synology/docker/ai/ollama/models` |
| Config | `/mnt/synology/docker/ai/ollama` |

---

## Model Management

### Recommended Models for 16GB VRAM

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `llama3.2` | 8B | ~5GB | General purpose |
| `mistral` | 7B | ~4GB | Fast, good quality |
| `codellama` | 7B | ~4GB | Code generation |
| `phi3` | 3B | ~2GB | Fast, smaller tasks |
| `llama3.2:3b` | 3B | ~2GB | Light workloads |

!!! warning "VRAM Limits"
    The RTX2000E ADA has 16GB VRAM. Models larger than ~12GB will fail to load or fall back to CPU (very slow).

### Create Custom Model

```bash
# Create a Modelfile
cat > /tmp/Modelfile << 'EOF'
FROM llama3.2
SYSTEM "You are a helpful homelab assistant."
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
EOF

# Create the model
docker exec -i ollama ollama create homelab-assistant < /tmp/Modelfile

# Use the custom model
docker exec -it ollama ollama run homelab-assistant
```

---

## Open-WebUI

Open-WebUI provides a ChatGPT-like interface at [chat.rsdn.io](https://chat.rsdn.io).

### Features

- Multi-user support with authentication
- Conversation history
- Model selection
- System prompts and presets
- Document upload for RAG

### First-Time Setup

1. Visit [chat.rsdn.io](https://chat.rsdn.io)
2. Create an account (first user becomes admin)
3. Select a model from the dropdown
4. Start chatting

---

## Troubleshooting

### Model Fails to Load

1. **Check VRAM availability:**
   ```bash
   ssh ctr01 'nvidia-smi'
   ```
   If VRAM is full, unload models or choose smaller model.

2. **Check disk space:**
   ```bash
   df -h /mnt/synology/docker/ai/ollama
   ```

3. **View Ollama logs:**
   ```bash
   ssh ctr01 'docker logs ollama --tail 100'
   ```

### Slow Inference

1. **Verify GPU is being used:**
   ```bash
   # Should show ollama process using GPU
   ssh ctr01 'nvidia-smi'
   ```

2. **Check if model fits in VRAM:**
   ```bash
   docker exec ollama ollama ps
   ```
   If "Processor" shows "CPU", model is too large.

3. **Reduce context size:**
   ```bash
   docker exec -it ollama ollama run llama3.2 --num-ctx 2048
   ```

### GPU Not Detected

1. **Verify NVIDIA drivers:**
   ```bash
   ssh ctr01 'nvidia-smi'
   ```

2. **Check Docker GPU runtime:**
   ```bash
   ssh ctr01 'docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi'
   ```

3. **Verify container has GPU access:**
   ```bash
   docker inspect ollama | grep -A 10 DeviceRequests
   ```

### API Connection Refused

1. **Check Ollama is running:**
   ```bash
   ssh ctr01 'docker ps | grep ollama'
   ```

2. **Verify port is listening:**
   ```bash
   ssh ctr01 'ss -tlnp | grep 11434'
   ```

3. **Test locally:**
   ```bash
   ssh ctr01 'curl http://localhost:11434/api/tags'
   ```

### Out of Memory (OOM)

If Ollama crashes with OOM:

1. **Use smaller model:**
   ```bash
   docker exec ollama ollama run phi3  # 3B instead of 8B
   ```

2. **Reduce context window:**
   ```bash
   docker exec -it ollama ollama run llama3.2 --num-ctx 1024
   ```

3. **Unload unused models:**
   ```bash
   # Models auto-unload after 5 minutes, or restart Ollama
   docker restart ollama
   ```

---

## Metrics and Monitoring

### GPU Metrics

```bash
# Real-time GPU stats
ssh ctr01 'nvidia-smi dmon -s pucvmet'

# GPU memory by process
ssh ctr01 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'
```

### Inference Stats

The API response includes timing information:

```json
{
  "total_duration": 5000000000,
  "load_duration": 100000000,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 500000000,
  "eval_count": 50,
  "eval_duration": 4400000000
}
```

---

## Related

- [AI Stack](../stacks/ctr01.md#ai)
- [VM Platform](../infrastructure/vm-platform.md) - GPU passthrough configuration
- [Ollama Official Docs](https://ollama.ai/docs)
- [Open-WebUI Docs](https://docs.openwebui.com/)
