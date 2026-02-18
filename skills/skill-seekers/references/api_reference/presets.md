# API Reference: presets.py

**Language**: Python

**Source**: `src\skill_seekers\cli\presets.py`

---

## Classes

### AnalysisPreset

Analysis preset configuration.

Defines a complete analysis configuration including depth,
feature flags, and AI enhancement level.

**Inherits from**: (none)



### PresetManager

Manages analysis presets and applies them to CLI arguments.

**Inherits from**: (none)

#### Methods

##### get_preset(name: str) → AnalysisPreset | None

Get preset by name.

Args:
    name: Preset name (case-insensitive)

Returns:
    AnalysisPreset if found, None otherwise

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| name | str | - | - |

**Returns**: `AnalysisPreset | None`


##### list_presets() → list[str]

List available preset names.

Returns:
    List of preset names in definition order

**Decorators**: `@staticmethod`

**Returns**: `list[str]`


##### format_preset_help() → str

Format preset help text for CLI.

Returns:
    Formatted help text with preset descriptions

**Decorators**: `@staticmethod`

**Returns**: `str`


##### apply_preset(preset_name: str, args: dict) → dict

Apply preset to args, with CLI overrides.

Preset defaults are applied first, then CLI arguments override
specific values. This allows users to customize presets.

Args:
    preset_name: Preset to apply
    args: Existing args from CLI (may contain overrides)

Returns:
    Updated args with preset applied

Raises:
    ValueError: If preset_name is unknown

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| preset_name | str | - | - |
| args | dict | - | - |

**Returns**: `dict`


##### get_default_preset() → str

Get the default preset name.

Returns:
    Default preset name ("standard")

**Decorators**: `@staticmethod`

**Returns**: `str`



