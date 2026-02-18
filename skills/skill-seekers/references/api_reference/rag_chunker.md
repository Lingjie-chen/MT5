# API Reference: rag_chunker.py

**Language**: Python

**Source**: `src\skill_seekers\cli\rag_chunker.py`

---

## Classes

### RAGChunker

Semantic chunker for RAG pipelines.

Features:
- Preserves code blocks (don't split mid-code)
- Preserves paragraphs (semantic boundaries)
- Adds metadata (source, category, chunk_id)
- Configurable chunk size and overlap

**Inherits from**: (none)

#### Methods

##### __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, preserve_code_blocks: bool = True, preserve_paragraphs: bool = True, min_chunk_size: int = 100)

Initialize RAG chunker.

Args:
    chunk_size: Target chunk size in tokens (approximate)
    chunk_overlap: Overlap size between chunks in tokens
    preserve_code_blocks: Keep code blocks intact
    preserve_paragraphs: Split at paragraph boundaries
    min_chunk_size: Minimum chunk size (avoid tiny chunks)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunk_size | int | 512 | - |
| chunk_overlap | int | 50 | - |
| preserve_code_blocks | bool | True | - |
| preserve_paragraphs | bool | True | - |
| min_chunk_size | int | 100 | - |


##### estimate_tokens(self, text: str) → int

Estimate token count for text.

Uses simple heuristic: ~4 chars per token for English.

Args:
    text: Text to estimate

Returns:
    Estimated token count

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `int`


##### chunk_document(self, text: str, metadata: dict, source_file: str | None = None) → list[dict]

Chunk single document into RAG-ready chunks.

Args:
    text: Document content
    metadata: Source metadata (url, category, etc.)
    source_file: Optional source filename

Returns:
    List of chunks with metadata

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| metadata | dict | - | - |
| source_file | str | None | None | - |

**Returns**: `list[dict]`


##### chunk_skill(self, skill_dir: Path) → list[dict]

Chunk entire skill directory.

Args:
    skill_dir: Path to skill directory (contains SKILL.md and references/)

Returns:
    List of all chunks with metadata

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |

**Returns**: `list[dict]`


##### _extract_code_blocks(self, text: str) → tuple[str, list[dict]]

Extract code blocks and replace with placeholders.

Args:
    text: Document content

Returns:
    Tuple of (text with placeholders, list of code blocks)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `tuple[str, list[dict]]`


##### _reinsert_code_blocks(self, chunks: list[str], code_blocks: list[dict]) → list[str]

Re-insert code blocks into chunks.

Args:
    chunks: Text chunks with placeholders
    code_blocks: Extracted code blocks

Returns:
    Chunks with code blocks re-inserted

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | list[str] | - | - |
| code_blocks | list[dict] | - | - |

**Returns**: `list[str]`


##### _find_semantic_boundaries(self, text: str) → list[int]

Find paragraph and section boundaries.

Args:
    text: Document content

Returns:
    List of character positions for boundaries (sorted)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `list[int]`


##### _split_with_overlap(self, text: str, boundaries: list[int]) → list[str]

Split text at semantic boundaries with overlap.

Args:
    text: Document content
    boundaries: Character positions for boundaries

Returns:
    List of text chunks

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| boundaries | list[int] | - | - |

**Returns**: `list[str]`


##### save_chunks(self, chunks: list[dict], output_path: Path) → None

Save chunks to JSON file.

Args:
    chunks: List of chunks with metadata
    output_path: Output file path

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | list[dict] | - | - |
| output_path | Path | - | - |

**Returns**: `None`




## Functions

### main()

CLI entry point for testing RAG chunker.

**Returns**: (none)



### replacer(match)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| match | None | - | - |

**Returns**: (none)


