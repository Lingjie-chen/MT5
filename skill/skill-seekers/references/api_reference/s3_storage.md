# API Reference: s3_storage.py

**Language**: Python

**Source**: `src\skill_seekers\cli\storage\s3_storage.py`

---

## Classes

### S3StorageAdaptor

AWS S3 storage adaptor.

Configuration:
    bucket: S3 bucket name (required)
    region: AWS region (optional, default: us-east-1)
    aws_access_key_id: AWS access key (optional, uses env/credentials)
    aws_secret_access_key: AWS secret key (optional, uses env/credentials)
    endpoint_url: Custom endpoint URL (optional, for S3-compatible services)

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    AWS_DEFAULT_REGION: AWS region

Examples:
    # Using environment variables
    adaptor = S3StorageAdaptor(bucket='my-bucket')

    # With explicit credentials
    adaptor = S3StorageAdaptor(
        bucket='my-bucket',
        region='us-west-2',
        aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
        aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    )

    # S3-compatible service (MinIO, DigitalOcean Spaces)
    adaptor = S3StorageAdaptor(
        bucket='my-bucket',
        endpoint_url='https://nyc3.digitaloceanspaces.com',
        aws_access_key_id='...',
        aws_secret_access_key='...'
    )

**Inherits from**: BaseStorageAdaptor

#### Methods

##### __init__(self)

Initialize S3 storage adaptor.

Args:
    bucket: S3 bucket name (required)
    **kwargs: Additional S3 configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### upload_file(self, local_path: str, remote_path: str, metadata: dict[str, str] | None = None) → str

Upload file to S3.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| local_path | str | - | - |
| remote_path | str | - | - |
| metadata | dict[str, str] | None | None | - |

**Returns**: `str`


##### download_file(self, remote_path: str, local_path: str) → None

Download file from S3.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| local_path | str | - | - |

**Returns**: `None`


##### delete_file(self, remote_path: str) → None

Delete file from S3.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `None`


##### list_files(self, prefix: str = '', max_results: int = 1000) → list[StorageObject]

List files in S3 bucket.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prefix | str | '' | - |
| max_results | int | 1000 | - |

**Returns**: `list[StorageObject]`


##### file_exists(self, remote_path: str) → bool

Check if file exists in S3.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `bool`


##### get_file_url(self, remote_path: str, expires_in: int = 3600) → str

Generate presigned URL for S3 object.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| expires_in | int | 3600 | - |

**Returns**: `str`


##### copy_file(self, source_path: str, dest_path: str) → None

Copy file within S3 bucket (server-side copy).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source_path | str | - | - |
| dest_path | str | - | - |

**Returns**: `None`



