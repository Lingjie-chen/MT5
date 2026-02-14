# API Reference: quickstart.py

**Language**: Python

**Source**: `examples\pinecone-upsert\quickstart.py`

---

## Functions

### create_index(pc: Pinecone, index_name: str, dimension: int = 1536) → None

Create Pinecone index if it doesn't exist.

Args:
    pc: Pinecone client
    index_name: Name of the index
    dimension: Embedding dimension (1536 for OpenAI ada-002)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| pc | Pinecone | - | - |
| index_name | str | - | - |
| dimension | int | 1536 | - |

**Returns**: `None`



### load_documents(json_path: str) → List[Dict]

Load documents from Skill Seekers JSON output.

Args:
    json_path: Path to skill-seekers generated JSON file

Returns:
    List of document dictionaries

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| json_path | str | - | - |

**Returns**: `List[Dict]`



### create_embeddings(openai_client: OpenAI, texts: List[str]) → List[List[float]]

Create embeddings for a list of texts.

Args:
    openai_client: OpenAI client
    texts: List of texts to embed

Returns:
    List of embedding vectors

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| openai_client | OpenAI | - | - |
| texts | List[str] | - | - |

**Returns**: `List[List[float]]`



### batch_upsert(index, openai_client: OpenAI, documents: List[Dict], batch_size: int = 100) → None

Upsert documents to Pinecone in batches.

Args:
    index: Pinecone index
    openai_client: OpenAI client
    documents: List of documents
    batch_size: Number of documents per batch

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| index | None | - | - |
| openai_client | OpenAI | - | - |
| documents | List[Dict] | - | - |
| batch_size | int | 100 | - |

**Returns**: `None`



### semantic_search(index, openai_client: OpenAI, query: str, top_k: int = 5, category: str = None) → List[Dict]

Perform semantic search.

Args:
    index: Pinecone index
    openai_client: OpenAI client
    query: Search query
    top_k: Number of results
    category: Optional category filter

Returns:
    List of matches

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| index | None | - | - |
| openai_client | OpenAI | - | - |
| query | str | - | - |
| top_k | int | 5 | - |
| category | str | None | - |

**Returns**: `List[Dict]`



### interactive_search(index, openai_client: OpenAI) → None

Start an interactive search session.

Args:
    index: Pinecone index
    openai_client: OpenAI client

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| index | None | - | - |
| openai_client | OpenAI | - | - |

**Returns**: `None`



### main()

Main execution flow.

**Returns**: (none)


