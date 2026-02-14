# API Reference: qdrant.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\qdrant.py`

---

## Classes

### QdrantAdaptor

Qdrant vector database adaptor.

Provides format conversion for:
- Qdrant collections (vector + payload format)
- Point-based storage with metadata payloads
- REST API compatible output
- Collection configuration with distance metrics

Note: Qdrant supports rich metadata payloads with filtering.

**Inherits from**: SkillAdaptor

#### Methods

##### _generate_point_id(self, content: str, metadata: dict) → str

Generate deterministic point ID from content and metadata.

Args:
    content: Document content
    metadata: Document metadata

Returns:
    UUID string (version 5, deterministic)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |

**Returns**: `str`


##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as Qdrant collection JSON.

Creates a package with:
- collection_name: Collection identifier
- points: Array of point objects (id, vector, payload)
- config: Collection configuration (vector size, distance metric)

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters

Returns:
    JSON string containing Qdrant-compatible data

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for Qdrant.

Creates a JSON file containing points, payloads, and config.

Args:
    skill_dir: Path to skill directory
    output_path: Output path/filename for JSON file

Returns:
    Path to created JSON file

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| output_path | Path | - | - |
| enable_chunking | bool | False | - |
| chunk_max_tokens | int | 512 | - |
| preserve_code_blocks | bool | True | - |

**Returns**: `Path`


##### upload(self, package_path: Path, _api_key: str) → dict[str, Any]

Qdrant format does not support direct upload via this tool.

Users should use the Qdrant client library or REST API.
Metadata is stored in payloads (native Qdrant feature).

Args:
    package_path: Path to JSON file
    api_key: Not used (Qdrant can use API keys for cloud)
    **kwargs: Not used

Returns:
    Result with usage instructions

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| package_path | Path | - | - |
| _api_key | str | - | - |

**Returns**: `dict[str, Any]`


##### validate_api_key(self, _api_key: str) → bool

Qdrant Cloud uses API keys, local instances don't.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _api_key | str | - | - |

**Returns**: `bool`


##### get_env_var_name(self) → str

Qdrant Cloud API key (optional).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

Qdrant format doesn't support AI enhancement.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### enhance(self, _skill_dir: Path, _api_key: str) → bool

Qdrant format doesn't support enhancement.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _skill_dir | Path | - | - |
| _api_key | str | - | - |

**Returns**: `bool`



