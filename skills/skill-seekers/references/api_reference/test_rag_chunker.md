# API Reference: test_rag_chunker.py

**Language**: Python

**Source**: `tests\test_rag_chunker.py`

---

## Classes

### TestRAGChunker

Test suite for RAGChunker class.

**Inherits from**: (none)

#### Methods

##### test_initialization(self)

Test RAGChunker initialization with default parameters.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_initialization_custom_params(self)

Test RAGChunker initialization with custom parameters.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_estimate_tokens(self)

Test token estimation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_chunk_document_empty(self)

Test chunking empty document.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_chunk_document_simple(self)

Test chunking simple document.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_preserve_code_blocks(self)

Test code block preservation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_code_block_not_split(self)

Test that code blocks are not split across chunks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_semantic_boundaries(self)

Test that chunks respect paragraph boundaries.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_chunk_overlap(self)

Test chunk overlap functionality.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_chunk_skill_directory(self, tmp_path)

Test chunking entire skill directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_save_chunks(self, tmp_path)

Test saving chunks to JSON file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_min_chunk_size(self)

Test that very small chunks are filtered out.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_extract_code_blocks(self)

Test code block extraction.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_find_semantic_boundaries(self)

Test semantic boundary detection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_real_world_documentation(self)

Test with realistic documentation content.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestRAGChunkerIntegration

Integration tests for RAG chunker with actual skills.

**Inherits from**: (none)

#### Methods

##### test_chunk_then_load_with_langchain(self, tmp_path)

Test that chunks can be loaded by LangChain.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_chunk_then_load_with_llamaindex(self, tmp_path)

Test that chunks can be loaded by LlamaIndex.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |



