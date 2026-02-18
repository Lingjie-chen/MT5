# API Reference: chroma.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\chroma.py`

---

## Classes

### ChromaAdaptor

Chroma vector database adaptor.

Handles:
- Chroma-compatible document format
- ID generation for documents
- Metadata structure
- Collection configuration hints
- Persistent collection support

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

Format skill as JSON for Chroma ingestion.

Converts SKILL.md and all references/*.md into Chroma-compatible format:
{
  "documents": [...],
  "metadatas": [...],
  "ids": [...]
}

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters (chunk_max_tokens, preserve_code_blocks)

Returns:
    JSON string containing Chroma-compatible data

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for Chroma.

Creates a JSON file containing documents, metadatas, and ids ready
for Chroma collection import.

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

Upload packaged skill to ChromaDB.

Args:
    package_path: Path to packaged JSON
    api_key: Not used for Chroma (uses URL instead)
    **kwargs:
        chroma_url: ChromaDB URL (default: http://localhost:8000)
        collection_name: Override collection name
        distance_function: "cosine", "l2", or "ip" (default: "cosine")
        embedding_function: "openai", "sentence-transformers", or None
        openai_api_key: For OpenAI embeddings
        persist_directory: Local directory for persistent storage

Returns:
    {"success": bool, "message": str, "collection": str, "count": int}

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

Chroma format doesn't use API keys for packaging.

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

No API key needed for Chroma packaging.

Returns:
    Empty string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

Chroma format doesn't support AI enhancement.

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

Chroma format doesn't support enhancement.

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



