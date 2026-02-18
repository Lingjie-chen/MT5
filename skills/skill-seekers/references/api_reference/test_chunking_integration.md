# API Reference: test_chunking_integration.py

**Language**: Python

**Source**: `tests\test_chunking_integration.py`

---

## Classes

### TestChunkingDisabledByDefault

Test that chunking is disabled by default.

**Inherits from**: (none)

#### Methods

##### test_langchain_no_chunking_default(self, tmp_path)

Test that LangChain doesn't chunk by default.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestChunkingEnabled

Test that chunking works when enabled.

**Inherits from**: (none)

#### Methods

##### test_langchain_chunking_enabled(self, tmp_path)

Test that LangChain chunks large documents when enabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_chunking_preserves_small_docs(self, tmp_path)

Test that small documents are not chunked.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestCodeBlockPreservation

Test that code blocks are preserved during chunking.

**Inherits from**: (none)

#### Methods

##### test_preserve_code_blocks(self, tmp_path)

Test that code blocks are not split during chunking.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestAutoChunkingForRAGPlatforms

Test that chunking is auto-enabled for RAG platforms.

**Inherits from**: (none)

#### Methods

##### test_rag_platforms_auto_chunk(self, platform, tmp_path)

Test that RAG platforms auto-enable chunking.

**Decorators**: `@pytest.mark.parametrize('platform', ['langchain'])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| platform | None | - | - |
| tmp_path | None | - | - |




### TestBaseAdaptorChunkingHelper

Test the base adaptor's _maybe_chunk_content method.

**Inherits from**: (none)

#### Methods

##### test_maybe_chunk_content_disabled(self)

Test that _maybe_chunk_content returns single chunk when disabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_maybe_chunk_content_small_doc(self)

Test that small docs are not chunked even when enabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_maybe_chunk_content_large_doc(self)

Test that large docs are chunked when enabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestChunkingCLIIntegration

Test chunking via CLI arguments.

**Inherits from**: (none)

#### Methods

##### test_chunk_flag(self, tmp_path)

Test --chunk flag enables chunking.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_chunk_tokens_parameter(self, tmp_path)

Test --chunk-tokens parameter controls chunk size.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




## Functions

### create_test_skill(tmp_path: Path, large_doc: bool = False) → Path

Create a test skill directory for chunking tests.

Args:
    tmp_path: Temporary directory
    large_doc: If True, create a large document (>512 tokens)

Returns:
    Path to skill directory

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| tmp_path | Path | - | - |
| large_doc | bool | False | - |

**Returns**: `Path`


