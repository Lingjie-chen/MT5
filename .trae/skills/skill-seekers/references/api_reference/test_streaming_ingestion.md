# API Reference: test_streaming_ingestion.py

**Language**: Python

**Source**: `tests\test_streaming_ingestion.py`

---

## Functions

### temp_skill_dir()

Create temporary skill directory for testing.

**Returns**: (none)



### test_chunk_document_single_chunk()

Test chunking when document fits in single chunk.

**Returns**: (none)



### test_chunk_document_multiple_chunks()

Test chunking with multiple chunks.

**Returns**: (none)



### test_chunk_document_metadata()

Test chunk metadata is correct.

**Returns**: (none)



### test_stream_skill_directory(temp_skill_dir)

Test streaming entire skill directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_batch_iterator()

Test batch processing.

**Returns**: (none)



### test_progress_tracking(temp_skill_dir)

Test progress tracking during streaming.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_checkpoint_save_load()

Test checkpoint save and load.

**Returns**: (none)



### test_format_progress()

Test progress formatting.

**Returns**: (none)



### test_empty_directory()

Test handling empty directory.

**Returns**: (none)



### test_chunk_size_validation()

Test different chunk sizes.

**Returns**: (none)



### callback(progress: IngestionProgress)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| progress | IngestionProgress | - | - |

**Returns**: (none)


