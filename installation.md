# Sony Projector ADCP - Complete Installation Guide

## Directory Structure

Create the following directory structure in your Home Assistant configuration folder:

```
config/
└── custom_components/
    └── sony_projector_adcp/
        ├── __init__.py
        ├── manifest.json
        ├── const.py
        ├── protocol.py
        ├── config_flow.py
        ├── media_player.py
        ├── services.yaml
        └── strings.json
```

## File Contents

You'll need to create these 8 files. Copy the contents from the artifacts provided.

## Installation Steps

1. **Create the directory**:
   ```bash
   cd /config  # or wherever your Home Assistant config is
   mkdir -p custom_components/sony_projector_adcp
   ```

2. **Copy all files** into the `custom_components/sony_projector_adcp/` directory

3. **Restart Home Assistant**

4. **Add the integration**:
   - Go to Settings → Devices & Services
   - Click "+ ADD INTEGRATION"
   - Search for "Sony Projector ADCP"
   - Enter your projector details:
     - IP Address: Your projector's IP (e.g., 192.168.1.100)
     - Port: 53595 (default)
     - Name: Sony Projector (or whatever you prefer)
     - Use Authentication: Yes (default)
     - Password: Projector (default, or your custom password)

## Projector Setup

Before configuring Home Assistant, ensure your Sony VPL-XW5000 is properly set up:

1. **Connect projector to network**:
   - Go to projector menu
   - Navigate to Installation → Network Settings
   - Set IP address (or use DHCP)
   - Note the IP address

2. **Enable network control**:
   - Set "Network Management" to ON
   - OR set "Standby Mode" to "Standard"
   - This allows the projector to respond to network commands even when in standby

3. **Check authentication settings**:
   - Note the authentication password (default is "Projector")
   - This is usually the same as the web interface password

## What You Get

After installation, you'll have **one media player entity** with all controls accessible via services:

### Media Player Entity
- `media_player.sony_projector`
  - Standard controls: power on/off, input selection
  - Attributes show current settings: brightness, contrast, picture mode, etc.

### Custom Services
All additional controls are accessed through services:

- `sony_projector_adcp.send_key` - Menu navigation (up, down, left, right, enter, menu, reset, blank)
- `sony_projector_adcp.set_picture_mode` - Select picture preset
- `sony_projector_adcp.set_brightness` - Adjust brightness (0-100)
- `sony_projector_adcp.set_contrast` - Adjust contrast (0-100)
- `sony_projector_adcp.set_sharpness` - Adjust sharpness (0-100)
- `sony_projector_adcp.set_light_output` - Adjust light output (0-100)

## Testing

### 1. Test Power Control
```yaml
service: media_player.turn_on
target:
  entity_id: media_player.sony_projector
```

### 2. Test Input Switching
```yaml
service: media_player.select_source
target:
  entity_id: media_player.sony_projector
data:
  source: "HDMI 1"
```

### 3. Test Picture Mode
```yaml
service: sony_projector_adcp.set_picture_mode
target:
  entity_id: media_player.sony_projector
data:
  mode: cinema_film1
```

### 4. Test Brightness
```yaml
service: sony_projector_adcp.set_brightness
target:
  entity_id: media_player.sony_projector
data:
  value: 75
```

### 5. Test Menu Navigation
```yaml
service: sony_projector_adcp.send_key
target:
  entity_id: media_player.sony_projector
data:
  key: menu
```

## Important Note: Volume Control

**⚠️ The VPL-XW5000 does not support volume control** according to Sony's ADCP protocol documentation. This is a hardware/firmware limitation of the projector model itself, not the integration. The protocol manual clearly shows that volume commands (`vol+`, `vol-`, `muting`) are not supported for this model.

If you need volume control, it must be handled by your audio receiver or other audio equipment in your setup.

## Troubleshooting

### Integration doesn't appear
- Check that all files are in the correct directory
- Restart Home Assistant
- Check the logs: Settings → System → Logs

### Cannot connect to projector
- Ping the projector IP from Home Assistant host
- Check projector network settings
- Verify Network Management is ON
- Check firewall settings
- Ensure port 53595 is accessible

### Authentication fails
- Verify password is correct (case-sensitive)
- Default password is "Projector"
- Check if authentication is enabled on projector
- Try disabling authentication in integration config if not needed

### Commands don't work
- Projector must be powered on for most commands
- Check logs for specific error messages
- Ensure projector firmware is up to date
- Wait 30 seconds after power-on before sending other commands

### Services don't appear
- Make sure `services.yaml` is in the correct directory
- Restart Home Assistant
- Check Developer Tools → Services for `sony_projector_adcp.*` services

## Advanced Configuration

### Custom Polling Interval
Edit `const.py` and change:
```python
SCAN_INTERVAL = 30  # Change to desired seconds
```

### Debug Logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.sony_projector_adcp: debug
```

### Adding More Input Sources
If your model has more HDMI inputs, edit `const.py`:
```python
INPUT_SOURCES = {
    "hdmi1": "HDMI 1",
    "hdmi2": "HDMI 2",
    "hdmi3": "HDMI 3",  # Add if available
    "hdmi4": "HDMI 4",  # Add if available
}
```

## Example Automation

Complete movie night setup:

```yaml
automation:
  - alias: "Movie Night Setup"
    trigger:
      - platform: state
        entity_id: input_boolean.movie_mode
        to: "on"
    action:
      # Power on
      - service: media_player.turn_on
        target:
          entity_id: media_player.sony_projector
      
      # Wait for warmup
      - delay:
          seconds: 30
      
      # Set input
      - service: media_player.select_source
        target:
          entity_id: media_player.sony_projector
        data:
          source: "HDMI 1"
      
      # Set picture mode
      - service: sony_projector_adcp.set_picture_mode
        target:
          entity_id: media_player.sony_projector
        data:
          mode: cinema_film1
      
      # Adjust picture settings
      - service: sony_projector_adcp.set_brightness
        target:
          entity_id: media_player.sony_projector
        data:
          value: 50
      
      - service: sony_projector_adcp.set_contrast
        target:
          entity_id: media_player.sony_projector
        data:
          value: 80
```

## Support

- Check Home Assistant logs for errors
- Review the ADCP protocol manual for command reference
- Ensure projector model is compatible
- Verify all network settings are correct

## Notes

- The integration polls the projector every 30 seconds for status updates
- Most settings require the projector to be powered on
- Some features may vary by projector model
- Current values are shown as attributes on the media player entity