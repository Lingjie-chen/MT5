# API Reference: weaviate.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\weaviate.py`

---

## Classes

### WeaviateAdaptor

Weaviate vector database adaptor.

Handles:
- Weaviate object format with properties
- Auto-generated schema definition
- UUID generation for objects
- Cross-reference support
- Metadata as properties for filtering
- Hybrid search optimization (vector + keyword)

**Inherits from**: SkillAdaptor

#### Methods

##### _generate_uuid(self, content: str, metadata: dict) → str

Generate deterministic UUID from content and metadata.

Args:
    content: Document content
    metadata: Document metadata

Returns:
    UUID string (RFC 4122 format)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |

**Returns**: `str`


##### _generate_schema(self, class_name: str) → dict

Generate Weaviate schema for documentation class.

Args:
    class_name: Name of the Weaviate class (e.g., "DocumentationChunk")

Returns:
    Schema dictionary

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| class_name | str | - | - |

**Returns**: `dict`


##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as JSON for Weaviate ingestion.

Converts SKILL.md and all references/*.md into Weaviate objects:
{
  "objects": [...],
  "schema": {...}
}

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters

Returns:
    JSON string containing Weaviate objects and schema

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for Weaviate.

Creates a JSON file containing:
- Schema definition
- Objects ready for batch import
- Helper metadata

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


##### upload(self, package_path: Path, api_key: str = None) → dict[str, Any]

Upload packaged skill to Weaviate.

Args:
    package_path: Path to packaged JSON
    api_key: Weaviate API key (for Weaviate Cloud)
    **kwargs:
        weaviate_url: Weaviate URL (default: http://localhost:8080)
        use_cloud: Use Weaviate Cloud (default: False)
        cluster_url: Weaviate Cloud cluster URL
        embedding_function: "openai", "sentence-transformers", or None
        openai_api_key: For OpenAI embeddings

Returns:
    {"success": bool, "message": str, "class_name": str, "count": int}

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| package_path | Path | - | - |
| api_key | str | None | - |

**Returns**: `dict[str, Any]`


##### _generate_openai_embeddings(self, documents: list[str], api_key: str = None) → list[list[float]]

Generate embeddings using OpenAI API.

Args:
    documents: List of document texts
    api_key: OpenAI API key (or uses OPENAI_API_KEY env var)

Returns:
    List of embedding vectors

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| documents | list[str] | - | - |
| api_key | str | None | - |

**Returns**: `list[list[float]]`


##### validate_api_key(self, _api_key: str) → bool

Weaviate format doesn't use API keys for packaging.

Args:
    api_key: Not used

Returns:
    Always False (no API needed for packaging)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _api_key | str | - | - |

**Returns**: `bool`


##### get_env_var_name(self) → str

No API key needed for Weaviate packaging.

Returns:
    Empty string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

Weaviate format doesn't support AI enhancement.

Enhancement should be done before conversion using:
skill-seekers enhance output/skill/ --mode LOCAL

Returns:
    False

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### enhance(self, _skill_dir: Path, _api_key: str) → bool

Weaviate format doesn't support enhancement.

Args:
    skill_dir: Not used
    api_key: Not used

Returns:
    False

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| _skill_dir | Path | - | - |
| _api_key | str | - | - |

**Returns**: `bool`



