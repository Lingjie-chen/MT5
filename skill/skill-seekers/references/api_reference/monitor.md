# API Reference: monitor.py

**Language**: Python

**Source**: `src\skill_seekers\sync\monitor.py`

---

## Classes

### SyncMonitor

Monitors documentation for changes and triggers updates.

Features:
- Continuous monitoring with configurable intervals
- State persistence (resume after restart)
- Change detection and diff generation
- Notification system
- Auto-update capability

Examples:
    # Basic usage
    monitor = SyncMonitor(
        config_path="configs/react.json",
        check_interval=3600
    )
    monitor.start()

    # With auto-update
    monitor = SyncMonitor(
        config_path="configs/react.json",
        auto_update=True,
        on_change=lambda report: print(f"Detected {report.change_count} changes")
    )

    # Run once
    changes = monitor.check_now()

**Inherits from**: (none)

#### Methods

##### __init__(self, config_path: str, check_interval: int = 3600, auto_update: bool = False, state_file: str | None = None, on_change: Callable[[ChangeReport], None] | None = None)

Initialize sync monitor.

Args:
    config_path: Path to skill config file
    check_interval: Check interval in seconds
    auto_update: Auto-rebuild skill on changes
    state_file: Path to state file (default: {skill_name}_sync.json)
    on_change: Callback function for change events

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config_path | str | - | - |
| check_interval | int | 3600 | - |
| auto_update | bool | False | - |
| state_file | str | None | None | - |
| on_change | Callable[[ChangeReport], None] | None | None | - |


##### _load_state(self) → SyncState

Load state from file or create new.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `SyncState`


##### _save_state(self)

Save current state to file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### check_now(self, generate_diffs: bool = False) → ChangeReport

Check for changes now (synchronous).

Args:
    generate_diffs: Whether to generate content diffs

Returns:
    ChangeReport with detected changes

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| generate_diffs | bool | False | - |

**Returns**: `ChangeReport`


##### _notify(self, report: ChangeReport)

Send notifications about changes.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| report | ChangeReport | - | - |


##### _trigger_update(self, report: ChangeReport)

Trigger skill rebuild.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| report | ChangeReport | - | - |


##### start(self)

Start continuous monitoring.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### stop(self)

Stop monitoring.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### stats(self) → dict

Get monitoring statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict`


##### __enter__(self)

Context manager entry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### __exit__(self, exc_type, exc_val, exc_tb)

Context manager exit.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| exc_type | None | - | - |
| exc_val | None | - | - |
| exc_tb | None | - | - |




## Functions

### run_schedule()

**Returns**: (none)


