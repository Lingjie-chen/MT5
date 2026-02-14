# API Reference: langchain.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\langchain.py`

---

## Classes

### LangChainAdaptor

LangChain platform adaptor.

Handles:
- LangChain Document format (page_content + metadata)
- JSON packaging with array of documents
- No upload (users import directly into code)
- Optimized for RAG/vector store ingestion

**Inherits from**: SkillAdaptor

#### Methods

##### format_skill_md(self, skill_dir: Path, metadata: SkillMetadata, enable_chunking: bool = False) → str

Format skill as JSON array of LangChain Documents.

Converts SKILL.md and all references/*.md into LangChain Document format:
{
  "page_content": "...",
  "metadata": {"source": "...", "category": "...", ...}
}

Args:
    skill_dir: Path to skill directory
    metadata: Skill metadata
    enable_chunking: Enable intelligent chunking for large documents
    **kwargs: Additional chunking parameters (chunk_max_tokens, preserve_code_blocks)

Returns:
    JSON string containing array of LangChain Documents

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| metadata | SkillMetadata | - | - |
| enable_chunking | bool | False | - |

**Returns**: `str`


##### package(self, skill_dir: Path, output_path: Path, enable_chunking: bool = False, chunk_max_tokens: int = 512, preserve_code_blocks: bool = True) → Path

Package skill into JSON file for LangChain.

Creates a JSON file containing an array of LangChain Documents ready
for ingestion into vector stores (Chroma, Pinecone, etc.)

Args:
    skill_dir: Path to skill directory
    output_path: Output path/filename for JSON file
    enable_chunking: Enable intelligent chunking for large documents
    chunk_max_tokens: Maximum tokens per chunk (default: 512)
    preserve_code_blocks: Preserve code blocks during chunking

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

LangChain format does not support direct upload.

Users should import the JSON file into their LangChain code:

```python
from langchain.schema import Document
import json

# Load documents
with open("skill-langchain.json") as f:
    docs_data = json.load(f)

# Convert to LangChain Documents
documents = [
    Document(page_content=doc["page_content"], metadata=doc["metadata"])
    for doc in docs_data
]

# Use with vector store
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_documents(documents, OpenAIEmbeddings())
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

LangChain format doesn't use API keys for packaging.

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

No API key needed for LangChain packaging.

Returns:
    Empty string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### supports_enhancement(self) → bool

LangChain format doesn't support AI enhancement.

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

LangChain format doesn't support enhancement.

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



