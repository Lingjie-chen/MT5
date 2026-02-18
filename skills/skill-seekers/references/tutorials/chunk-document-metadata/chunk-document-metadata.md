# How To: Chunk Document Metadata

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test chunk metadata is correct.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`


## Step-by-Step Guide

### Step 1: 'Test chunk metadata is correct.'

```python
'Test chunk metadata is correct.'
```

**Verification:**
```python
assert chunk_meta.chunk_index == i
```

### Step 2: Assign ingester = StreamingIngester(...)

```python
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
```

**Verification:**
```python
assert chunk_meta.total_chunks == len(chunks)
```

### Step 3: Assign content = value

```python
content = 'B' * 250
```

**Verification:**
```python
assert chunk_meta.source == 'test_source'
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test_source', 'file': 'test_file.md', 'category': 'test_cat'}
```

**Verification:**
```python
assert chunk_meta.file == 'test_file.md'
```

### Step 5: Assign chunks = list(...)

```python
chunks = list(ingester.chunk_document(content, metadata))
```

**Verification:**
```python
assert chunk_meta.category == 'test_cat'
```


## Complete Example

```python
# Workflow
'Test chunk metadata is correct.'
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
content = 'B' * 250
metadata = {'source': 'test_source', 'file': 'test_file.md', 'category': 'test_cat'}
chunks = list(ingester.chunk_document(content, metadata))
for i, (chunk_text, chunk_meta) in enumerate(chunks):
    assert chunk_meta.chunk_index == i
    assert chunk_meta.total_chunks == len(chunks)
    assert chunk_meta.source == 'test_source'
    assert chunk_meta.file == 'test_file.md'
    assert chunk_meta.category == 'test_cat'
    assert len(chunk_meta.chunk_id) == 32
```

## Next Steps


---

*Source: test_streaming_ingestion.py:87 | Complexity: Intermediate | Last updated: 2026-02-14*