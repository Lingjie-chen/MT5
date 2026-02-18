# How To: Chunk Document Multiple Chunks

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test chunking with multiple chunks.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`


## Step-by-Step Guide

### Step 1: 'Test chunking with multiple chunks.'

```python
'Test chunking with multiple chunks.'
```

**Verification:**
```python
assert len(chunks) > 1
```

### Step 2: Assign ingester = StreamingIngester(...)

```python
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
```

**Verification:**
```python
assert chunk2_meta.char_start < chunk1_meta.char_end
```

### Step 3: Assign content = value

```python
content = 'A' * 250
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
```

### Step 5: Assign chunks = list(...)

```python
chunks = list(ingester.chunk_document(content, metadata))
```

**Verification:**
```python
assert len(chunks) > 1
```

### Step 6: Assign unknown = value

```python
chunk1_text, chunk1_meta = chunks[i]
```

### Step 7: Assign unknown = value

```python
chunk2_text, chunk2_meta = chunks[i + 1]
```

**Verification:**
```python
assert chunk2_meta.char_start < chunk1_meta.char_end
```


## Complete Example

```python
# Workflow
'Test chunking with multiple chunks.'
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
content = 'A' * 250
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
chunks = list(ingester.chunk_document(content, metadata))
assert len(chunks) > 1
for i in range(len(chunks) - 1):
    chunk1_text, chunk1_meta = chunks[i]
    chunk2_text, chunk2_meta = chunks[i + 1]
    assert chunk2_meta.char_start < chunk1_meta.char_end
```

## Next Steps


---

*Source: test_streaming_ingestion.py:66 | Complexity: Intermediate | Last updated: 2026-02-14*