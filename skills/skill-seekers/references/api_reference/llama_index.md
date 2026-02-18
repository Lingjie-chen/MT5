# API Reference: llama_index.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\llama_index.py`

---

## Classes

### LlamaIndexAdaptor

LlamaIndex platform adaptor.

Handles:
- LlamaIndex Node format (text + metadata + id)
- JSON packaging with array of nodes
- No upload (users import directly into code)
- Optimized for query engines and indexes

**Inherits from**: SkillAdaptor

#### Methods

##### _generate_node_id(self, content: str, metadata: dict) → str

Generate a stable unique ID for a node.

Args:
    content: Node content
    metadata: Node metadata

Returns:
    Unique node ID (hash-based)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |

**Returns**: `str`


##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as JSON array of LlamaIndex Nodes.

Converts SKILL.md and all references/*.md into LlamaIndex Node format:
{
  "text": "...",
  "metadata": {"source": "...", "category": "...", ...},
  "id_": "unique-hash-id",
  "embedding": null
}

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters (chunk_max_tokens, preserve_code_blocks)

Returns:
    JSON string containing array of LlamaIndex Nodes

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for LlamaIndex.

Creates a JSON file containing an array of LlamaIndex Nodes ready
for creating indexes, query engines, or vector stores.

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

LlamaIndex format does not support direct upload.

Users should import the JSON file into their LlamaIndex code:

```python
from llama_index.core.schema import TextNode
import json

# Load nodes
with open("skill-llama-index.json") as f:
    nodes_data = json.load(f)

# Convert to LlamaIndex Nodes
nodes = [
    TextNode(
        text=node["text"],
        metadata=node["metadata"],
        id_=node["id_"]
    )
    for node in nodes_data
]

# Create index
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()

# Query
response = query_engine.query("your question here")
```

Args:
    package_path: Path to JSON file
    api_key: Not used
    **kwargs: Not used

Returns:
    Result indicating no upload capability

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| package_path | Path | - | - |
| _api_key | str | - | - |

**Returns**: `dict[str, Any]`


##### validate_api_key(self, _api_key: str) → bool

LlamaIndex format doesn't use API keys for packaging.

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

No API key needed for LlamaIndex packaging.

Returns:
    Empty string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

LlamaIndex format doesn't support AI enhancement.

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

LlamaIndex format doesn't support enhancement.

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



