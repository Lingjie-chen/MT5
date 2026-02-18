# How To: Cost Stats

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test cost statistics tracking.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.embedding_pipeline`


## Step-by-Step Guide

### Step 1: 'Test cost statistics tracking.'

```python
'Test cost statistics tracking.'
```

**Verification:**
```python
assert 'total_requests' in stats
```

### Step 2: Assign config = EmbeddingConfig(...)

```python
config = EmbeddingConfig(provider='local', model='test-model', dimension=64)
```

**Verification:**
```python
assert 'cache_hits' in stats
```

### Step 3: Assign pipeline = EmbeddingPipeline(...)

```python
pipeline = EmbeddingPipeline(config)
```

**Verification:**
```python
assert 'estimated_cost' in stats
```

### Step 4: Assign texts = value

```python
texts = ['doc 1', 'doc 2']
```

### Step 5: Call pipeline.generate_batch()

```python
pipeline.generate_batch(texts, show_progress=False)
```

### Step 6: Assign stats = pipeline.get_cost_stats(...)

```python
stats = pipeline.get_cost_stats()
```

**Verification:**
```python
assert 'total_requests' in stats
```


## Complete Example

```python
# Workflow
'Test cost statistics tracking.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=64)
pipeline = EmbeddingPipeline(config)
texts = ['doc 1', 'doc 2']
pipeline.generate_batch(texts, show_progress=False)
stats = pipeline.get_cost_stats()
assert 'total_requests' in stats
assert 'cache_hits' in stats
assert 'estimated_cost' in stats
```

## Next Steps


---

*Source: test_embedding_pipeline.py:235 | Complexity: Intermediate | Last updated: 2026-02-14*