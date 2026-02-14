# API Reference: config_validator.py

**Language**: Python

**Source**: `src\skill_seekers\cli\config_validator.py`

---

## Classes

### ConfigValidator

Validates unified config format (legacy support removed in v2.11.0).

**Inherits from**: (none)

#### Methods

##### __init__(self, config_or_path: dict[str, Any] | str)

Initialize validator with config dict or file path.

Args:
    config_or_path: Either a config dict or path to config JSON file

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config_or_path | dict[str, Any] | str | - | - |


##### _load_config(self) → dict[str, Any]

Load JSON config file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`


##### validate(self) → bool

Validate unified config format.

Returns:
    True if valid

Raises:
    ValueError if invalid with detailed error message

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### _validate_unified(self) → bool

Validate unified config format.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### _validate_source(self, source: dict[str, Any], index: int)

Validate individual source configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source | dict[str, Any] | - | - |
| index | int | - | - |


##### _validate_documentation_source(self, source: dict[str, Any], index: int)

Validate documentation source configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source | dict[str, Any] | - | - |
| index | int | - | - |


##### _validate_github_source(self, source: dict[str, Any], index: int)

Validate GitHub source configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source | dict[str, Any] | - | - |
| index | int | - | - |


##### _validate_pdf_source(self, source: dict[str, Any], index: int)

Validate PDF source configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source | dict[str, Any] | - | - |
| index | int | - | - |


##### _validate_local_source(self, source: dict[str, Any], index: int)

Validate local codebase source configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source | dict[str, Any] | - | - |
| index | int | - | - |


##### get_sources_by_type(self, source_type: str) → list[dict[str, Any]]

Get all sources of a specific type.

Args:
    source_type: 'documentation', 'github', 'pdf', or 'local'

Returns:
    List of sources matching the type

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source_type | str | - | - |

**Returns**: `list[dict[str, Any]]`


##### has_multiple_sources(self) → bool

Check if config has multiple sources (requires merging).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### needs_api_merge(self) → bool

Check if config needs API merging.

Returns True if both documentation and github sources exist
with API extraction enabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`




## Functions

### validate_config(config_path: str) → ConfigValidator

Validate config file and return validator instance.

Args:
    config_path: Path to config JSON file

Returns:
    ConfigValidator instance

Raises:
    ValueError if config is invalid

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| config_path | str | - | - |

**Returns**: `ConfigValidator`


