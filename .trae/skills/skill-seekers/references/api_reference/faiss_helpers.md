# API Reference: faiss_helpers.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\faiss_helpers.py`

---

## Classes

### FAISSHelpers

FAISS helper adaptor.

Provides utilities for:
- FAISS index creation (multiple types)
- Metadata management (JSON storage - safe and portable)
- Save/load indexes with metadata
- Batch document addition
- Search with metadata filtering
- Index optimization

Note: FAISS doesn't have built-in metadata support, so we manage it separately.

**Inherits from**: SkillAdaptor

#### Methods

##### _generate_id(self, content: str, metadata: dict) → str

Generate deterministic ID from content and metadata.

Args:
    content: Document content
    metadata: Document metadata

Returns:
    ID string (hex digest)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |

**Returns**: `str`


##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as JSON for FAISS ingestion.

Creates a package with:
- documents: Array of document strings
- metadatas: Array of metadata dicts
- ids: Array of IDs
- config: FAISS configuration hints

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters

Returns:
    JSON string containing FAISS-compatible data

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for FAISS.

Creates a JSON file containing documents, metadata, and FAISS config.

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

FAISS format does not support direct upload.

Users should import the JSON file and create FAISS index.
Metadata is stored as JSON (safe and portable).

Args:
    package_path: Path to JSON file
    api_key: Not used
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

FAISS doesn't use API keys.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _api_key | str | - | - |

**Returns**: `bool`


##### get_env_var_name(self) → str

FAISS doesn't use API keys.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

FAISS format doesn't support AI enhancement.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### enhance(self, _skill_dir: Path, _api_key: str) → bool

FAISS format doesn't support enhancement.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _skill_dir | Path | - | - |
| _api_key | str | - | - |

**Returns**: `bool`



