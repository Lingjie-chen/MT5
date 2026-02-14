# How To: Chunk Size Validation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test different chunk sizes.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`


## Step-by-Step Guide

### Step 1: 'Test different chunk sizes.'

```python
'Test different chunk sizes.'
```

**Verification:**
```python
assert len(chunks_small) > len(chunks_large)
```

### Step 2: Assign content = value

```python
content = 'X' * 1000
```

### Step 3: Assign ingester_small = StreamingIngester(...)

```python
ingester_small = StreamingIngester(chunk_size=100, chunk_overlap=10)
```

### Step 4: Assign chunks_small = list(...)

```python
chunks_small = list(ingester_small.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
```

### Step 5: Assign ingester_large = StreamingIngester(...)

```python
ingester_large = StreamingIngester(chunk_size=500, chunk_overlap=50)
```

### Step 6: Assign chunks_large = list(...)

```python
chunks_large = list(ingester_large.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
```

**Verification:**
```python
assert len(chunks_small) > len(chunks_large)
```


## Complete Example

```python
# Workflow
'Test different chunk sizes.'
content = 'X' * 1000
ingester_small = StreamingIngester(chunk_size=100, chunk_overlap=10)
chunks_small = list(ingester_small.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
ingester_large = StreamingIngester(chunk_size=500, chunk_overlap=50)
chunks_large = list(ingester_large.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
assert len(chunks_small) > len(chunks_large)
```

## Next Steps


---

*Source: test_streaming_ingestion.py:243 | Complexity: Intermediate | Last updated: 2026-02-14*