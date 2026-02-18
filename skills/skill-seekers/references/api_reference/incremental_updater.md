# API Reference: incremental_updater.py

**Language**: Python

**Source**: `src\skill_seekers\cli\incremental_updater.py`

---

## Classes

### DocumentVersion

Version information for a document.

**Inherits from**: (none)



### ChangeSet

Set of changes detected.

**Inherits from**: (none)

#### Methods

##### has_changes(self) → bool

Check if there are any changes.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### total_changes(self) → int

Count total changes.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`




### UpdateMetadata

Metadata for an incremental update.

**Inherits from**: (none)



### IncrementalUpdater

Manages incremental updates for skill documentation.

Tracks document versions, detects changes, and generates
delta packages for efficient updates.

**Inherits from**: (none)

#### Methods

##### __init__(self, skill_dir: Path, version_file: str = '.skill_version.json')

Initialize incremental updater.

Args:
    skill_dir: Path to skill directory
    version_file: Name of version tracking file

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| version_file | str | '.skill_version.json' | - |


##### _compute_file_hash(self, file_path: Path) → str

Compute SHA256 hash of file content.

Args:
    file_path: Path to file

Returns:
    Hex digest of SHA256 hash

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| file_path | Path | - | - |

**Returns**: `str`


##### _scan_documents(self) → dict[str, DocumentVersion]

Scan skill directory and build version map.

Returns:
    Dictionary mapping file paths to versions

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, DocumentVersion]`


##### load_previous_versions(self) → bool

Load previous version information from disk.

Returns:
    True if versions loaded, False if no previous versions

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### save_current_versions(self) → None

Save current version information to disk.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `None`


##### detect_changes(self) → ChangeSet

Detect changes between previous and current versions.

Returns:
    ChangeSet describing all changes

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `ChangeSet`


##### generate_update_package(self, change_set: ChangeSet, output_path: Path, include_content: bool = True) → Path

Generate incremental update package.

Args:
    change_set: Changes to include
    output_path: Output path for package
    include_content: Include full document content

Returns:
    Path to created package

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| change_set | ChangeSet | - | - |
| output_path | Path | - | - |
| include_content | bool | True | - |

**Returns**: `Path`


##### generate_diff_report(self, change_set: ChangeSet) → str

Generate human-readable diff report.

Args:
    change_set: Changes to report

Returns:
    Formatted report string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| change_set | ChangeSet | - | - |

**Returns**: `str`


##### apply_update_package(self, package_path: Path) → bool

Apply an incremental update package.

Args:
    package_path: Path to update package

Returns:
    True if successful

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| package_path | Path | - | - |

**Returns**: `bool`




## Functions

### main()

CLI entry point for incremental updates.

**Returns**: (none)


