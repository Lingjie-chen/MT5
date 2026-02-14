# API Reference: streaming_ingest.py

**Language**: Python

**Source**: `src\skill_seekers\cli\streaming_ingest.py`

---

## Classes

### ChunkMetadata

Metadata for a document chunk.

**Inherits from**: (none)



### IngestionProgress

Progress tracking for streaming ingestion.

**Inherits from**: (none)

#### Methods

##### progress_percent(self) → float

Calculate progress percentage.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### elapsed_time(self) → float

Calculate elapsed time in seconds.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### chunks_per_second(self) → float

Calculate processing rate.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### eta_seconds(self) → float

Estimate time remaining in seconds.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`




### StreamingIngester

Streaming ingestion manager for large documentation sets.

Provides memory-efficient processing with chunking, progress tracking,
and resume capabilities.

**Inherits from**: (none)

#### Methods

##### __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200, batch_size: int = 100, max_memory_mb: int = 500)

Initialize streaming ingester.

Args:
    chunk_size: Maximum characters per chunk
    chunk_overlap: Overlap between chunks (for context)
    batch_size: Number of chunks per batch
    max_memory_mb: Maximum memory usage in MB

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunk_size | int | 4000 | - |
| chunk_overlap | int | 200 | - |
| batch_size | int | 100 | - |
| max_memory_mb | int | 500 | - |


##### chunk_document(self, content: str, metadata: dict, chunk_size: int | None = None, chunk_overlap: int | None = None) → Iterator[tuple[str, ChunkMetadata]]

Split document into overlapping chunks.

Args:
    content: Document content
    metadata: Document metadata
    chunk_size: Override default chunk size
    chunk_overlap: Override default overlap

Yields:
    Tuple of (chunk_text, chunk_metadata)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |
| chunk_size | int | None | None | - |
| chunk_overlap | int | None | None | - |

**Returns**: `Iterator[tuple[str, ChunkMetadata]]`


##### _generate_chunk_id(self, content: str, metadata: dict, chunk_index: int) → str

Generate deterministic chunk ID.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |
| metadata | dict | - | - |
| chunk_index | int | - | - |

**Returns**: `str`


##### stream_skill_directory(self, skill_dir: Path, callback: Callable | None = None) → Iterator[tuple[str, dict]]

Stream all documents from skill directory.

Args:
    skill_dir: Path to skill directory
    callback: Optional progress callback(progress: IngestionProgress)

Yields:
    Tuple of (chunk_text, chunk_metadata_dict)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| callback | Callable | None | None | - |

**Returns**: `Iterator[tuple[str, dict]]`


##### batch_iterator(self, chunks: Iterator[tuple[str, dict]], batch_size: int | None = None) → Iterator[list[tuple[str, dict]]]

Group chunks into batches for efficient processing.

Args:
    chunks: Iterator of (chunk_text, chunk_metadata) tuples
    batch_size: Override default batch size

Yields:
    List of chunks (batch)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | Iterator[tuple[str, dict]] | - | - |
| batch_size | int | None | None | - |

**Returns**: `Iterator[list[tuple[str, dict]]]`


##### save_checkpoint(self, checkpoint_path: Path, state: dict) → None

Save ingestion checkpoint for resume capability.

Args:
    checkpoint_path: Path to checkpoint file
    state: State dictionary to save

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| checkpoint_path | Path | - | - |
| state | dict | - | - |

**Returns**: `None`


##### load_checkpoint(self, checkpoint_path: Path) → dict | None

Load ingestion checkpoint for resume.

Args:
    checkpoint_path: Path to checkpoint file

Returns:
    State dictionary or None if not found

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| checkpoint_path | Path | - | - |

**Returns**: `dict | None`


##### format_progress(self) → str

Format progress as human-readable string.

Returns:
    Progress string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`




## Functions

### main()

CLI entry point for streaming ingestion.

**Returns**: (none)



### on_progress(progress: IngestionProgress)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| progress | IngestionProgress | - | - |

**Returns**: (none)


