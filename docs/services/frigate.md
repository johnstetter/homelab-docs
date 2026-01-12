# Frigate

Network Video Recorder (NVR) with GPU-accelerated object detection.

## Access

| Property | Value |
|----------|-------|
| **URL** | [frigate.rsdn.io](https://frigate.rsdn.io) |
| **Stack** | [compose-stacks/frigate](https://gitlab.com/stetter-homelab/compose-stacks/frigate) |
| **Ports** | 5000 (Web), 8554 (RTSP), 8555 (WebRTC) |
| **Image** | `ghcr.io/blakeblackshear/frigate:0.16.3-tensorrt` |
| **GPU** | NVIDIA RTX2000E ADA (TensorRT) |

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌────────────────┐
│   Cameras   │────▶│  Frigate │────▶│ Home Assistant │
│  (RTSP)     │     │  (GPU)   │     │    (MQTT)      │
└─────────────┘     └──────────┘     └────────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         PostgreSQL    Redis     Storage
                                  (NFS)
```

---

## Common Operations

### View Live Cameras

1. Go to [frigate.rsdn.io](https://frigate.rsdn.io)
2. Click camera name to view live feed
3. Toggle between live view and recordings

### View Recordings

1. Go to [frigate.rsdn.io](https://frigate.rsdn.io)
2. Click **Recordings** in sidebar
3. Select camera and time range
4. Click timeline to jump to specific time

### View Events

1. Click **Events** in sidebar
2. Filter by:
   - Camera
   - Object type (person, car, etc.)
   - Time range
3. Click event for clip playback

### Export a Clip

1. Navigate to the event or recording
2. Use timeline to select start/end
3. Click **Export** button
4. Download MP4 file

---

## Configuration

### Config File Location

`/mnt/synology/docker/frigate/config/config.yml`

### Basic Camera Setup

```yaml
cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@192.168.1.100:554/stream
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      enabled: true
      retain:
        days: 7
    snapshots:
      enabled: true
```

### Object Detection

```yaml
detectors:
  tensorrt:
    type: tensorrt
    device: 0  # GPU device

objects:
  track:
    - person
    - car
    - dog
    - cat
  filters:
    person:
      min_score: 0.6
      threshold: 0.7
```

### Motion Zones

Define zones to limit detection areas:

```yaml
cameras:
  front_door:
    zones:
      driveway:
        coordinates: 0,500,800,500,800,0,0,0
        objects:
          - car
      porch:
        coordinates: 800,500,1920,500,1920,0,800,0
        objects:
          - person
```

### MQTT Integration

```yaml
mqtt:
  enabled: true
  host: mqtt.rsdn.io
  port: 1883
  user: "{FRIGATE_MQTT_USER}"
  password: "{FRIGATE_MQTT_PASSWORD}"
```

---

## Home Assistant Integration

### MQTT Discovery

Frigate auto-publishes to MQTT. Home Assistant discovers:
- Camera entities
- Binary sensors (motion, person detected)
- Event sensors

### Frigate Card

Install the [Frigate Card](https://github.com/dermotduffy/frigate-hass-card) for rich camera UI.

```yaml
type: custom:frigate-card
cameras:
  - camera_entity: camera.front_door
    live_provider: go2rtc
```

### Automation Example

```yaml
automation:
  - alias: "Notify on Person Detected"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door_person_occupancy
      to: "on"
    action:
      service: notify.mobile_app
      data:
        message: "Person detected at front door"
        data:
          image: "{{ state_attr('camera.front_door', 'entity_picture') }}"
```

---

## Data Storage

| Path | Description |
|------|-------------|
| `/mnt/synology/docker/frigate/config` | Configuration |
| `/mnt/synology/docker/frigate/media` | Recordings and snapshots |
| PostgreSQL volume | Event database |
| Redis volume | Cache and state |

### Retention Settings

```yaml
record:
  retain:
    days: 7        # Keep all recordings 7 days
    mode: motion   # Only keep motion events after 7 days

snapshots:
  retain:
    default: 14    # Keep snapshots 14 days
```

---

## GPU Acceleration

Frigate uses the RTX2000E ADA for:
- **Detection** - TensorRT inference
- **Decode** - NVDEC hardware decoding
- **Encode** - NVENC for re-streaming

### Check GPU Usage

```bash
# GPU utilization
ssh ctr01 'nvidia-smi'

# Frigate-specific
ssh ctr01 'docker exec frigate nvidia-smi'
```

---

## Troubleshooting

### Camera Not Connecting

```bash
# Test RTSP stream
ffprobe rtsp://user:pass@192.168.1.100:554/stream

# Check Frigate logs
docker logs frigate | grep -i "camera_name"
```

### High CPU Usage

1. Enable hardware decoding:
   ```yaml
   ffmpeg:
     hwaccel_args: preset-nvidia-h264
   ```
2. Reduce detect FPS
3. Lower resolution for detection stream

### No Detections

1. **Check detector status** in Frigate UI → System
2. **Verify GPU access:**
   ```bash
   docker exec frigate nvidia-smi
   ```
3. **Check object filters** - min_score might be too high

### Recording Issues

```bash
# Check disk space
df -h /mnt/synology/docker/frigate/media

# Check Frigate storage stats
curl -s http://localhost:5001/api/stats | jq .
```

### MQTT Not Connecting

1. Verify MQTT broker is running
2. Check credentials in config
3. Test MQTT connection:
   ```bash
   docker exec frigate mosquitto_sub -h mqtt.rsdn.io -u user -P pass -t 'frigate/#'
   ```

---

## Maintenance

### Restart Frigate

```bash
ssh ctr01 'cd /opt/stacks/frigate && docker compose restart frigate'
```

### Update Configuration

1. Edit `/mnt/synology/docker/frigate/config/config.yml`
2. Restart Frigate (config reloads on restart)

### Clear All Recordings

```bash
# Stop Frigate first
docker compose stop frigate

# Remove media
rm -rf /mnt/synology/docker/frigate/media/*

# Start Frigate
docker compose start frigate
```

---

## Related

- [Frigate Stack](../stacks/ctr01.md#frigate)
- [Frigate Docs](https://docs.frigate.video/)
- [Frigate Card](https://github.com/dermotduffy/frigate-hass-card)
- [Home Assistant](https://home-assistant.io/)
