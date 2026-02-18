# API Reference: base_storage.py

**Language**: Python

**Source**: `src\skill_seekers\cli\storage\base_storage.py`

---

## Classes

### StorageObject

Represents a file/object in cloud storage.

Attributes:
    key: Object key/path in storage
    size: Size in bytes
    last_modified: Last modification timestamp
    etag: ETag/hash of object
    metadata: Additional metadata

**Inherits from**: (none)



### BaseStorageAdaptor

Abstract base class for cloud storage adaptors.

Provides unified interface for different cloud storage providers.
All adaptors must implement these methods.

**Inherits from**: ABC

#### Methods

##### __init__(self)

Initialize storage adaptor.

Args:
    **kwargs: Provider-specific configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### upload_file(self, local_path: str, remote_path: str, metadata: dict[str, str] | None = None) → str

Upload file to cloud storage.

Args:
    local_path: Path to local file
    remote_path: Destination path in cloud storage
    metadata: Optional metadata to attach to file

Returns:
    URL or identifier of uploaded file

Raises:
    FileNotFoundError: If local file doesn't exist
    Exception: If upload fails

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| local_path | str | - | - |
| remote_path | str | - | - |
| metadata | dict[str, str] | None | None | - |

**Returns**: `str`


##### download_file(self, remote_path: str, local_path: str) → None

Download file from cloud storage.

Args:
    remote_path: Path to file in cloud storage
    local_path: Destination path for downloaded file

Raises:
    FileNotFoundError: If remote file doesn't exist
    Exception: If download fails

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| local_path | str | - | - |

**Returns**: `None`


##### delete_file(self, remote_path: str) → None

Delete file from cloud storage.

Args:
    remote_path: Path to file in cloud storage

Raises:
    FileNotFoundError: If remote file doesn't exist
    Exception: If deletion fails

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `None`


##### list_files(self, prefix: str = '', max_results: int = 1000) → list[StorageObject]

List files in cloud storage.

Args:
    prefix: Prefix to filter files (directory path)
    max_results: Maximum number of results to return

Returns:
    List of StorageObject instances

Raises:
    Exception: If listing fails

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prefix | str | '' | - |
| max_results | int | 1000 | - |

**Returns**: `list[StorageObject]`


##### file_exists(self, remote_path: str) → bool

Check if file exists in cloud storage.

Args:
    remote_path: Path to file in cloud storage

Returns:
    True if file exists, False otherwise

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `bool`


##### get_file_url(self, remote_path: str, expires_in: int = 3600) → str

Generate signed URL for file access.

Args:
    remote_path: Path to file in cloud storage
    expires_in: URL expiration time in seconds (default: 1 hour)

Returns:
    Signed URL for file access

Raises:
    FileNotFoundError: If remote file doesn't exist
    Exception: If URL generation fails

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| expires_in | int | 3600 | - |

**Returns**: `str`


##### upload_directory(self, local_dir: str, remote_prefix: str = '', exclude_patterns: list[str] | None = None) → list[str]

Upload entire directory to cloud storage.

Args:
    local_dir: Path to local directory
    remote_prefix: Prefix for uploaded files
    exclude_patterns: Glob patterns to exclude files

Returns:
    List of uploaded file paths

Raises:
    NotADirectoryError: If local_dir is not a directory
    Exception: If upload fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| local_dir | str | - | - |
| remote_prefix | str | '' | - |
| exclude_patterns | list[str] | None | None | - |

**Returns**: `list[str]`


##### download_directory(self, remote_prefix: str, local_dir: str) → list[str]

Download directory from cloud storage.

Args:
    remote_prefix: Prefix of files to download
    local_dir: Destination directory

Returns:
    List of downloaded file paths

Raises:
    Exception: If download fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_prefix | str | - | - |
| local_dir | str | - | - |

**Returns**: `list[str]`


##### get_file_size(self, remote_path: str) → int

Get size of file in cloud storage.

Args:
    remote_path: Path to file in cloud storage

Returns:
    File size in bytes

Raises:
    FileNotFoundError: If remote file doesn't exist

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `int`


##### copy_file(self, source_path: str, dest_path: str) → None

Copy file within cloud storage.

Default implementation downloads then uploads.
Subclasses can override with provider-specific copy operations.

Args:
    source_path: Source file path
    dest_path: Destination file path

Raises:
    FileNotFoundError: If source file doesn't exist
    Exception: If copy fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source_path | str | - | - |
| dest_path | str | - | - |

**Returns**: `None`



