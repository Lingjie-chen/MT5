# API Reference: azure_storage.py

**Language**: Python

**Source**: `src\skill_seekers\cli\storage\azure_storage.py`

---

## Classes

### AzureStorageAdaptor

Azure Blob Storage adaptor.

Configuration:
    container: Azure container name (required)
    account_name: Storage account name (optional, uses env)
    account_key: Storage account key (optional, uses env)
    connection_string: Connection string (optional, alternative to account_name/key)

Environment Variables:
    AZURE_STORAGE_CONNECTION_STRING: Azure storage connection string
    AZURE_STORAGE_ACCOUNT_NAME: Storage account name
    AZURE_STORAGE_ACCOUNT_KEY: Storage account key

Examples:
    # Using connection string
    adaptor = AzureStorageAdaptor(
        container='my-container',
        connection_string='DefaultEndpointsProtocol=https;...'
    )

    # Using account name and key
    adaptor = AzureStorageAdaptor(
        container='my-container',
        account_name='myaccount',
        account_key='mykey'
    )

    # Using environment variables
    adaptor = AzureStorageAdaptor(container='my-container')

**Inherits from**: BaseStorageAdaptor

#### Methods

##### __init__(self)

Initialize Azure storage adaptor.

Args:
    container: Azure container name (required)
    **kwargs: Additional Azure configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### upload_file(self, local_path: str, remote_path: str, metadata: dict[str, str] | None = None) → str

Upload file to Azure Blob Storage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| local_path | str | - | - |
| remote_path | str | - | - |
| metadata | dict[str, str] | None | None | - |

**Returns**: `str`


##### download_file(self, remote_path: str, local_path: str) → None

Download file from Azure Blob Storage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| local_path | str | - | - |

**Returns**: `None`


##### delete_file(self, remote_path: str) → None

Delete file from Azure Blob Storage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `None`


##### list_files(self, prefix: str = '', max_results: int = 1000) → list[StorageObject]

List files in Azure container.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prefix | str | '' | - |
| max_results | int | 1000 | - |

**Returns**: `list[StorageObject]`


##### file_exists(self, remote_path: str) → bool

Check if file exists in Azure Blob Storage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |

**Returns**: `bool`


##### get_file_url(self, remote_path: str, expires_in: int = 3600) → str

Generate SAS URL for Azure blob.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| remote_path | str | - | - |
| expires_in | int | 3600 | - |

**Returns**: `str`


##### copy_file(self, source_path: str, dest_path: str) → None

Copy file within Azure container (server-side copy).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| source_path | str | - | - |
| dest_path | str | - | - |

**Returns**: `None`



