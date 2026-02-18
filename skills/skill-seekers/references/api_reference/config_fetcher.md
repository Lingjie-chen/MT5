# API Reference: config_fetcher.py

**Language**: Python

**Source**: `src\skill_seekers\cli\config_fetcher.py`

---

## Functions

### fetch_config_from_api(config_name: str, destination: str = 'configs', timeout: float = 30.0) → Path | None

Fetch a config file from the SkillSeekersWeb.com API.

Args:
    config_name: Name of config to download (e.g., 'react', 'godot')
    destination: Directory to save config file (default: 'configs')
    timeout: Request timeout in seconds (default: 30.0)

Returns:
    Path to downloaded config file, or None if fetch failed

Example:
    >>> config_path = fetch_config_from_api('react')
    >>> if config_path:
    ...     print(f"Downloaded to {config_path}")

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| config_name | str | - | - |
| destination | str | 'configs' | - |
| timeout | float | 30.0 | - |

**Returns**: `Path | None`



### list_available_configs(category: str | None = None, timeout: float = 30.0) → list[str]

List all available configs from the API.

Args:
    category: Filter by category (optional)
    timeout: Request timeout in seconds (default: 30.0)

Returns:
    List of available config names

Example:
    >>> configs = list_available_configs()
    >>> print(f"Available: {', '.join(configs)}")

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| category | str | None | None | - |
| timeout | float | 30.0 | - |

**Returns**: `list[str]`



### resolve_config_path(config_path: str, auto_fetch: bool = True) → Path | None

Resolve config path with automatic API fallback.

Tries to find config in this order:
1. Exact path as provided
2. With 'configs/' prefix added (current directory)
3. User config directory (~/.config/skill-seekers/configs/)
4. Fetch from API (if auto_fetch=True)

Args:
    config_path: Config file path or name
    auto_fetch: Automatically fetch from API if not found locally (default: True)

Returns:
    Path to config file, or None if not found

Example:
    >>> path = resolve_config_path('react.json')
    >>> if path:
    ...     with open(path) as f:
    ...         config = json.load(f)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| config_path | str | - | - |
| auto_fetch | bool | True | - |

**Returns**: `Path | None`



### get_last_searched_paths() → list[Path]

Get the list of paths that were searched in the last resolve_config_path call.

Returns:
    List of absolute paths that were checked for the config file

Example:
    >>> resolve_config_path('myconfig.json', auto_fetch=False)
    >>> paths = get_last_searched_paths()
    >>> for p in paths:
    ...     print(f"Searched: {p}")

**Returns**: `list[Path]`


