# API Reference: haystack.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\haystack.py`

---

## Classes

### HaystackAdaptor

Haystack platform adaptor.

Handles:
- Haystack Document format (content + meta)
- JSON packaging with array of documents
- No upload (users import directly into code)
- Optimized for Haystack 2.x pipelines

**Inherits from**: SkillAdaptor

#### Methods

##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as JSON array of Haystack Documents.

Converts SKILL.md and all references/*.md into Haystack Document format:
{
  "content": "...",
  "meta": {"source": "...", "category": "...", ...}
}

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters

Returns:
    JSON string containing array of Haystack Documents

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for Haystack.

Creates a JSON file containing an array of Haystack Documents ready
for ingestion into Haystack 2.x pipelines and document stores.

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

Haystack format does not support direct upload.

Users should import the JSON file into their Haystack code:

```python
from haystack import Document
import json

# Load documents
with open("skill-haystack.json") as f:
    docs_data = json.load(f)

# Convert to Haystack Documents
documents = [
    Document(content=doc["content"], meta=doc["meta"])
    for doc in docs_data
]

# Use with document store
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()
document_store.write_documents(documents)

# Create pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

retriever = InMemoryBM25Retriever(document_store=document_store)
results = retriever.run(query="your query here")
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

Haystack format doesn't use API keys for packaging.

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

No API key needed for Haystack packaging.

Returns:
    Empty string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

Haystack format doesn't support AI enhancement.

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

Haystack format doesn't support enhancement.

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



