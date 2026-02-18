# API Reference: streaming_adaptor.py

**Language**: Python

**Source**: `src\skill_seekers\cli\adaptors\streaming_adaptor.py`

---

## Classes

### StreamingAdaptorMixin

Mixin class to add streaming capabilities to platform adaptors.

Provides:
- Chunked document processing
- Memory-efficient streaming
- Progress tracking
- Batch processing
- Resume capability

**Inherits from**: (none)

#### Methods

##### package_streaming(self, skill_dir: Path, output_path: Path, chunk_size: int = 4000, chunk_overlap: int = 200, batch_size: int = 100, progress_callback: Callable | None = None) → Path

Package skill using streaming ingestion.

Memory-efficient alternative to standard package() method.
Suitable for large documentation sets (>100 documents or >10MB).

Args:
    skill_dir: Path to skill directory
    output_path: Output path/filename
    chunk_size: Maximum characters per chunk
    chunk_overlap: Overlap between chunks (for context)
    batch_size: Number of chunks per batch
    progress_callback: Optional callback(progress: IngestionProgress)

Returns:
    Path to created package file

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| output_path | Path | - | - |
| chunk_size | int | 4000 | - |
| chunk_overlap | int | 200 | - |
| batch_size | int | 100 | - |
| progress_callback | Callable | None | None | - |

**Returns**: `Path`


##### _convert_chunks_to_platform_format(self, chunks: list[tuple[str, dict]], skill_name: str) → dict

Convert chunks to platform-specific format.

Subclasses should override this method to customize format.

Args:
    chunks: List of (chunk_text, chunk_metadata) tuples
    skill_name: Name of the skill

Returns:
    Platform-specific data structure

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | list[tuple[str, dict]] | - | - |
| skill_name | str | - | - |

**Returns**: `dict`


##### estimate_chunks(self, skill_dir: Path, chunk_size: int = 4000, chunk_overlap: int = 200) → dict[str, Any]

Estimate chunking for a skill directory.

Useful for planning and validation before processing.

Args:
    skill_dir: Path to skill directory
    chunk_size: Maximum characters per chunk
    chunk_overlap: Overlap between chunks

Returns:
    Estimation statistics

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |
| chunk_size | int | 4000 | - |
| chunk_overlap | int | 200 | - |

**Returns**: `dict[str, Any]`




### StreamingLangChainAdaptor

LangChain adaptor with streaming support.

**Inherits from**: StreamingAdaptorMixin

#### Methods

##### _convert_chunks_to_platform_format(self, chunks, skill_name)

Convert chunks to LangChain Document format.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | None | - | - |
| skill_name | None | - | - |




### StreamingChromaAdaptor

Chroma adaptor with streaming support.

**Inherits from**: StreamingAdaptorMixin

#### Methods

##### _convert_chunks_to_platform_format(self, chunks, skill_name)

Convert chunks to Chroma format.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| chunks | None | - | - |
| skill_name | None | - | - |




## Functions

### demo_streaming()

Demonstrate streaming ingestion.

**Returns**: (none)



### on_progress(progress: IngestionProgress)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| progress | IngestionProgress | - | - |

**Returns**: (none)


