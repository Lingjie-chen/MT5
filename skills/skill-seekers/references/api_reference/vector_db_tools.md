# API Reference: vector_db_tools.py

**Language**: Python

**Source**: `src\skill_seekers\mcp\tools\vector_db_tools.py`

---

## Classes

### TextContent

Fallback TextContent for when MCP is not installed

**Inherits from**: (none)

#### Methods

##### __init__(self, type: str, text: str)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| type | str | - | - |
| text | str | - | - |




## Functions

### export_to_weaviate_impl(args: dict) → list[TextContent]

**Async function**

Export skill to Weaviate vector database format.

Weaviate is a popular cloud-native vector database with hybrid search
(combining vector similarity + BM25 keyword search). Ideal for
production RAG applications with 450K+ users.

Args:
    args: Dictionary with:
        - skill_dir (str): Path to skill directory (e.g., output/react/)
        - output_dir (str, optional): Output directory (default: same as skill_dir)

Returns:
    List of TextContent with export results

Example:
    {
        "skill_dir": "output/react",
        "output_dir": "output"
    }

Output Format:
    JSON file with Weaviate schema:
    - class_name: Weaviate class name
    - schema: Property definitions
    - objects: Document objects with vectors and metadata
    - config: Distance metric configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | dict | - | - |

**Returns**: `list[TextContent]`



### export_to_chroma_impl(args: dict) → list[TextContent]

**Async function**

Export skill to Chroma vector database format.

Chroma is a popular open-source embedding database designed for
local-first development. Perfect for RAG prototyping with 800K+ developers.

Args:
    args: Dictionary with:
        - skill_dir (str): Path to skill directory (e.g., output/react/)
        - output_dir (str, optional): Output directory (default: same as skill_dir)

Returns:
    List of TextContent with export results

Example:
    {
        "skill_dir": "output/react",
        "output_dir": "output"
    }

Output Format:
    JSON file with Chroma collection data:
    - collection_name: Collection identifier
    - documents: List of document texts
    - metadatas: List of metadata dicts
    - ids: List of unique IDs

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | dict | - | - |

**Returns**: `list[TextContent]`



### export_to_faiss_impl(args: dict) → list[TextContent]

**Async function**

Export skill to FAISS vector index format.

FAISS (Facebook AI Similarity Search) is a library for efficient similarity
search at billion-scale. Supports GPU acceleration for ultra-fast search.

Args:
    args: Dictionary with:
        - skill_dir (str): Path to skill directory (e.g., output/react/)
        - output_dir (str, optional): Output directory (default: same as skill_dir)
        - index_type (str, optional): FAISS index type (default: 'Flat')
                                    Options: 'Flat', 'IVF', 'HNSW'

Returns:
    List of TextContent with export results

Example:
    {
        "skill_dir": "output/react",
        "output_dir": "output",
        "index_type": "HNSW"
    }

Output Format:
    JSON file with FAISS data:
    - embeddings: List of embedding vectors
    - metadata: List of document metadata
    - index_config: FAISS index configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | dict | - | - |

**Returns**: `list[TextContent]`



### export_to_qdrant_impl(args: dict) → list[TextContent]

**Async function**

Export skill to Qdrant vector database format.

Qdrant is a modern vector database with native payload filtering and
high-performance search. Ideal for production RAG with 100K+ users.

Args:
    args: Dictionary with:
        - skill_dir (str): Path to skill directory (e.g., output/react/)
        - output_dir (str, optional): Output directory (default: same as skill_dir)

Returns:
    List of TextContent with export results

Example:
    {
        "skill_dir": "output/react",
        "output_dir": "output"
    }

Output Format:
    JSON file with Qdrant collection data:
    - collection_name: Collection identifier
    - points: List of points with id, vector, payload
    - config: Vector configuration

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | dict | - | - |

**Returns**: `list[TextContent]`


