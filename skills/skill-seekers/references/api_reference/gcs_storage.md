# API Reference: gcs_storage.py

**Language**: Python

**Source**: `src\skill_seekers\cli\storage\gcs_storage.py`

---

## Classes

### GCSStorageAdaptor

Google Cloud Storage adaptor.

Configuration:
    bucket: GCS bucket name (required)
    project: GCP project ID (optional, uses default)
    credentials_path: Path to service account JSON (optional)

Environment Variables:
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON
    GOOGLE_CLOUD_PROJECT: GCP project ID

Examples:
    # Using environment variables
    adaptor = GCSStorageAdaptor(bucket='my-bucket')

    # With explicit credentials
    adaptor = GCSStorageAdaptor(
        bucket='my-bucket',
        project='my-project',
        credentials_path='/path/to/credentials.json'
    )

    # Using default credentials
    adaptor = GCSStorageAdaptor(
        bucket='my-bucket',
        project='my-project'
    )

**Inherits from**: BaseStorageAdaptor

#### Methods

##### __init__(self)

Initialize GCS storage adaptor.

Args:
    bucket: GCS bucket name (required)
    **kwargs: Additional GCS configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### upload_file(self, local_path: str, remote_path: str, metadata: dict[str, str] | None = None) → str

Upload file to GCS.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| local_path | str | - | - |
| remote_path | str | - | - |
| metadata | dict[str, str] | None | None | - |

**Returns**: `str`


##### download_file(self, remote_path: str, local_path: str) → None

Download file from GCS.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| local_path | str | - | - |

**Returns**: `None`


##### delete_file(self, remote_path: str) → None

Delete file from GCS.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `None`


##### list_files(self, prefix: str = '', max_results: int = 1000) → list[StorageObject]

List files in GCS bucket.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prefix | str | '' | - |
| max_results | int | 1000 | - |

**Returns**: `list[StorageObject]`


##### file_exists(self, remote_path: str) → bool

Check if file exists in GCS.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `bool`


##### get_file_url(self, remote_path: str, expires_in: int = 3600) → str

Generate signed URL for GCS object.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| expires_in | int | 3600 | - |

**Returns**: `str`


##### copy_file(self, source_path: str, dest_path: str) → None

Copy file within GCS bucket (server-side copy).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source_path | str | - | - |
| dest_path | str | - | - |

**Returns**: `None`



