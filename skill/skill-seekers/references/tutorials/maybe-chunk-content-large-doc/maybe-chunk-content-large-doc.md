# How To: Maybe Chunk Content Large Doc

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that large docs are chunked when enabled.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `pathlib`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.package_skill`


## Step-by-Step Guide

### Step 1: 'Test that large docs are chunked when enabled.'

```python
'Test that large docs are chunked when enabled.'
```

**Verification:**
```python
assert len(chunks) > 1, f'Large doc should be chunked, got {len(chunks)} chunks'
```

### Step 2: Assign adaptor = LangChainAdaptor(...)

```python
adaptor = LangChainAdaptor()
```

**Verification:**
```python
assert isinstance(chunk_text, str)
```

### Step 3: Assign content = value

```python
content = 'Lorem ipsum dolor sit amet. ' * 2000
```

**Verification:**
```python
assert isinstance(chunk_meta, dict)
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test', 'file': 'test.md'}
```

**Verification:**
```python
assert chunk_meta['is_chunked']
```

### Step 5: Assign chunks = adaptor._maybe_chunk_content(...)

```python
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512, preserve_code_blocks=True, source_file='test.md')
```

**Verification:**
```python
assert 'chunk_index' in chunk_meta
```


## Complete Example

```python
# Workflow
'Test that large docs are chunked when enabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Lorem ipsum dolor sit amet. ' * 2000
metadata = {'source': 'test', 'file': 'test.md'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512, preserve_code_blocks=True, source_file='test.md')
assert len(chunks) > 1, f'Large doc should be chunked, got {len(chunks)} chunks'
for chunk_text, chunk_meta in chunks:
    assert isinstance(chunk_text, str)
    assert isinstance(chunk_meta, dict)
    assert chunk_meta['is_chunked']
    assert 'chunk_index' in chunk_meta
    assert 'chunk_id' in chunk_meta
    assert chunk_meta['source'] == 'test'
    assert chunk_meta['file'] == 'test.md'
```

## Next Steps


---

*Source: test_chunking_integration.py:257 | Complexity: Intermediate | Last updated: 2026-02-14*