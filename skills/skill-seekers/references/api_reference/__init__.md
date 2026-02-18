# API Reference: __init__.py

**Language**: Python

**Source**: `src\skill_seekers\cli\storage\__init__.py`

---

## Functions

### get_storage_adaptor(provider: str) → BaseStorageAdaptor

Factory function to get storage adaptor for specified provider.

Args:
    provider: Storage provider name ('s3', 'gcs', 'azure')
    **kwargs: Provider-specific configuration

Returns:
    Storage adaptor instance

Raises:
    ValueError: If provider is not supported

Examples:
    # AWS S3
    adaptor = get_storage_adaptor('s3',
                                 bucket='my-bucket',
                                 region='us-west-2')

    # Google Cloud Storage
    adaptor = get_storage_adaptor('gcs',
                                 bucket='my-bucket',
                                 project='my-project')

    # Azure Blob Storage
    adaptor = get_storage_adaptor('azure',
                                 container='my-container',
                                 account_name='myaccount')

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| provider | str | - | - |

**Returns**: `BaseStorageAdaptor`


