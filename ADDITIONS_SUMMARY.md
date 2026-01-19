# New Features Added

## 1. Reality Creation Control

Reality Creation is Sony's upscaling and image enhancement technology.

### Services Added:
- `sony_projector_adcp.set_reality_creation` - Set Reality Creation on or off
- `sony_projector_adcp.toggle_reality_creation` - Toggle between on and off

### Attributes Added:
- `reality_creation` - Current state ("on" or "off")

### Usage Examples:

```yaml
# Turn on Reality Creation
service: sony_projector_adcp.set_reality_creation
target:
  entity_id: media_player.sony_projector
data:
  state: "on"

# Turn off Reality Creation
service: sony_projector_adcp.set_reality_creation
target:
  entity_id: media_player.sony_projector
data:
  state: "off"

# Toggle Reality Creation
service: sony_projector_adcp.toggle_reality_creation
target:
  entity_id: media_player.sony_projector

# Check current state in automation
{{ state_attr('media_player.sony_projector', 'reality_creation') }}
```

## 2. Raw Command Pass-through

Send any ADCP command directly to the projector for advanced control.

### Service Added:
- `sony_projector_adcp.send_raw_command` - Send raw ADCP commands

### Usage Examples:

```yaml
# Set color temperature
service: sony_projector_adcp.send_raw_command
target:
  entity_id: media_player.sony_projector
data:
  command: 'color_temp "d65"'

# Adjust film mode
service: sony_projector_adcp.send_raw_command
target:
  entity_id: media_player.sony_projector
data:
  command: 'film_mode "auto"'

# Set gamma correction
service: sony_projector_adcp.send_raw_command
target:
  entity_id: media_player.sony_projector
data:
  command: 'gamma_correction "2.2"'

# Query any value
service: sony_projector_adcp.send_raw_command
target:
  entity_id: media_player.sony_projector
data:
  command: 'color_temp ?'
```

### Command Format Guidelines:

**String parameters** (enclosed in quotes):
```yaml
command: 'picture_mode "cinema_film1"'
command: 'input "hdmi1"'
command: 'color_temp "d65"'
```

**Numeric parameters** (no quotes):
```yaml
command: 'brightness 75'
command: 'contrast 80'
command: 'sharpness 50'
```

**Queries** (add ? at the end):
```yaml
command: 'picture_mode ?'
command: 'brightness ?'
command: 'power_status ?'
```

### Important Notes:

⚠️ **Use with caution:**
- Commands must match exact ADCP protocol syntax
- Incorrect commands may fail silently or cause unexpected behavior
- Always test commands manually before using in automations
- Refer to Sony's ADCP Protocol Manual for complete command reference

✅ **Benefits:**
- Access any projector feature via ADCP protocol
- Test new features before they're implemented as services
- Create advanced calibration automations
- Full flexibility for power users

## Files Modified:

1. **const.py** - Added reality creation command constants
2. **protocol.py** - Added reality creation getter/setter methods
3. **media_player.py** - Added:
   - Reality creation state tracking
   - Service handlers for reality creation
   - Raw command pass-through service
4. **services.yaml** - Added service definitions for:
   - `set_reality_creation`
   - `toggle_reality_creation`
   - `send_raw_command`
5. **README.md** - Documented all new features with examples

## Testing:

### Test Reality Creation:
```yaml
# In Developer Tools > Services
service: sony_projector_adcp.set_reality_creation
target:
  entity_id: media_player.sony_projector
data:
  state: "on"

# Check attribute in Developer Tools > States
# Look at media_player.sony_projector attributes for "reality_creation"
```

### Test Raw Command:
```yaml
# In Developer Tools > Services
service: sony_projector_adcp.send_raw_command
target:
  entity_id: media_player.sony_projector
data:
  command: 'picture_mode ?'

# Check Home Assistant logs for the response
```

## Upgrade Instructions:

1. Replace the following files in `custom_components/sony_projector_adcp/`:
   - `const.py`
   - `protocol.py`
   - `media_player.py`
   - `services.yaml`
   - `README.md`

2. Restart Home Assistant

3. Test the new services in Developer Tools > Services

4. New services will appear as:
   - `sony_projector_adcp.set_reality_creation`
   - `sony_projector_adcp.toggle_reality_creation`
   - `sony_projector_adcp.send_raw_command`