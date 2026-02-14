# How To: Chunk Document Single Chunk

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test chunking when document fits in single chunk.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`


## Step-by-Step Guide

### Step 1: 'Test chunking when document fits in single chunk.'

```python
'Test chunking when document fits in single chunk.'
```

**Verification:**
```python
assert len(chunks) == 1
```

### Step 2: Assign ingester = StreamingIngester(...)

```python
ingester = StreamingIngester(chunk_size=1000, chunk_overlap=100)
```

**Verification:**
```python
assert chunk_text == content
```

### Step 3: Assign content = 'Small document'

```python
content = 'Small document'
```

**Verification:**
```python
assert chunk_meta.chunk_index == 0
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
```

**Verification:**
```python
assert chunk_meta.total_chunks == 1
```

### Step 5: Assign chunks = list(...)

```python
chunks = list(ingester.chunk_document(content, metadata))
```

**Verification:**
```python
assert chunk_meta.source == 'test'
```

### Step 6: Assign unknown = value

```python
chunk_text, chunk_meta = chunks[0]
```

**Verification:**
```python
assert chunk_text == content
```


## Complete Example

```python
# Workflow
'Test chunking when document fits in single chunk.'
ingester = StreamingIngester(chunk_size=1000, chunk_overlap=100)
content = 'Small document'
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
chunks = list(ingester.chunk_document(content, metadata))
assert len(chunks) == 1
chunk_text, chunk_meta = chunks[0]
assert chunk_text == content
assert chunk_meta.chunk_index == 0
assert chunk_meta.total_chunks == 1
assert chunk_meta.source == 'test'
```

## Next Steps


---

*Source: test_streaming_ingestion.py:48 | Complexity: Intermediate | Last updated: 2026-02-14*