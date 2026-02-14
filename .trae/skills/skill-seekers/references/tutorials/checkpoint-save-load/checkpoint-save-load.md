# How To: Checkpoint Save Load

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test checkpoint save and load.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.streaming_ingest`


## Step-by-Step Guide

### Step 1: 'Test checkpoint save and load.'

```python
'Test checkpoint save and load.'
```

**Verification:**
```python
assert checkpoint_path.exists()
```

### Step 2: Assign ingester = StreamingIngester(...)

```python
ingester = StreamingIngester()
```

**Verification:**
```python
assert loaded_state == state
```

### Step 3: Assign checkpoint_path = value

```python
checkpoint_path = Path(tmpdir) / 'checkpoint.json'
```

### Step 4: Assign ingester.progress = IngestionProgress(...)

```python
ingester.progress = IngestionProgress(total_documents=10, processed_documents=5, total_chunks=100, processed_chunks=50, failed_chunks=2, bytes_processed=10000, start_time=1234567890.0)
```

### Step 5: Assign state = value

```python
state = {'last_processed_file': 'test.md', 'batch_number': 3}
```

### Step 6: Call ingester.save_checkpoint()

```python
ingester.save_checkpoint(checkpoint_path, state)
```

**Verification:**
```python
assert checkpoint_path.exists()
```

### Step 7: Assign loaded_state = ingester.load_checkpoint(...)

```python
loaded_state = ingester.load_checkpoint(checkpoint_path)
```

**Verification:**
```python
assert loaded_state == state
```


## Complete Example

```python
# Workflow
'Test checkpoint save and load.'
ingester = StreamingIngester()
with tempfile.TemporaryDirectory() as tmpdir:
    checkpoint_path = Path(tmpdir) / 'checkpoint.json'
    ingester.progress = IngestionProgress(total_documents=10, processed_documents=5, total_chunks=100, processed_chunks=50, failed_chunks=2, bytes_processed=10000, start_time=1234567890.0)
    state = {'last_processed_file': 'test.md', 'batch_number': 3}
    ingester.save_checkpoint(checkpoint_path, state)
    assert checkpoint_path.exists()
    loaded_state = ingester.load_checkpoint(checkpoint_path)
    assert loaded_state == state
```

## Next Steps


---

*Source: test_streaming_ingestion.py:178 | Complexity: Intermediate | Last updated: 2026-02-14*