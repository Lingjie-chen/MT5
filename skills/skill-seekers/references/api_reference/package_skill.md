# API Reference: package_skill.py

**Language**: Python

**Source**: `src\skill_seekers\cli\package_skill.py`

---

## Functions

### package_skill(skill_dir, open_folder_after = True, skip_quality_check = False, target = 'claude', streaming = False, chunk_size = 4000, chunk_overlap = 200, batch_size = 100, enable_chunking = False, chunk_max_tokens = 512, preserve_code_blocks = True)

Package a skill directory into platform-specific format

Args:
    skill_dir: Path to skill directory
    open_folder_after: Whether to open the output folder after packaging
    skip_quality_check: Skip quality checks before packaging
    target: Target LLM platform ('claude', 'gemini', 'openai', 'markdown')
    streaming: Use streaming ingestion for large docs
    chunk_size: Maximum characters per chunk (streaming mode)
    chunk_overlap: Overlap between chunks (streaming mode)
    batch_size: Number of chunks per batch (streaming mode)
    enable_chunking: Enable intelligent chunking for RAG platforms
    chunk_max_tokens: Maximum tokens per chunk (default: 512)
    preserve_code_blocks: Preserve code blocks during chunking

Returns:
    tuple: (success, package_path) where success is bool and package_path is Path or None

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| skill_dir | None | - | - |
| open_folder_after | None | True | - |
| skip_quality_check | None | False | - |
| target | None | 'claude' | - |
| streaming | None | False | - |
| chunk_size | None | 4000 | - |
| chunk_overlap | None | 200 | - |
| batch_size | None | 100 | - |
| enable_chunking | None | False | - |
| chunk_max_tokens | None | 512 | - |
| preserve_code_blocks | None | True | - |

**Returns**: (none)



### main()

**Returns**: (none)


