# How To: Stream Skill Directory

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test streaming entire skill directory.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`

**Setup Required:**
```python
# Fixtures: temp_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Test streaming entire skill directory.'

```python
'Test streaming entire skill directory.'
```

**Verification:**
```python
assert len(chunks) > 0
```

### Step 2: Assign ingester = StreamingIngester(...)

```python
ingester = StreamingIngester(chunk_size=500, chunk_overlap=50)
```

**Verification:**
```python
assert ingester.progress is not None
```

### Step 3: Assign chunks = list(...)

```python
chunks = list(ingester.stream_skill_directory(temp_skill_dir))
```

**Verification:**
```python
assert ingester.progress.total_documents == 3
```

### Step 4: Assign sources = set(...)

```python
sources = set()
```

**Verification:**
```python
assert ingester.progress.processed_documents == 3
```

### Step 5: Assign categories = set(...)

```python
categories = set()
```

**Verification:**
```python
assert ingester.progress.total_chunks > 0
```

### Step 6: Call sources.add()

```python
sources.add(chunk_meta['source'])
```

**Verification:**
```python
assert ingester.progress.processed_chunks == len(chunks)
```

### Step 7: Call categories.add()

```python
categories.add(chunk_meta['category'])
```

**Verification:**
```python
assert chunk_text
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test streaming entire skill directory.'
ingester = StreamingIngester(chunk_size=500, chunk_overlap=50)
chunks = list(ingester.stream_skill_directory(temp_skill_dir))
assert len(chunks) > 0
assert ingester.progress is not None
assert ingester.progress.total_documents == 3
assert ingester.progress.processed_documents == 3
assert ingester.progress.total_chunks > 0
assert ingester.progress.processed_chunks == len(chunks)
sources = set()
categories = set()
for chunk_text, chunk_meta in chunks:
    assert chunk_text
    assert chunk_meta['chunk_id']
    sources.add(chunk_meta['source'])
    categories.add(chunk_meta['category'])
assert 'test_skill' in sources
assert 'overview' in categories
```

## Next Steps


---

*Source: test_streaming_ingestion.py:105 | Complexity: Intermediate | Last updated: 2026-02-14*