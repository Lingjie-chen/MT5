# How To: Validate Dimensions Invalid

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test dimension validation with invalid embeddings.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.embedding_pipeline`


## Step-by-Step Guide

### Step 1: 'Test dimension validation with invalid embeddings.'

```python
'Test dimension validation with invalid embeddings.'
```

**Verification:**
```python
assert not is_valid
```

### Step 2: Assign config = EmbeddingConfig(...)

```python
config = EmbeddingConfig(provider='local', model='test-model', dimension=128)
```

### Step 3: Assign pipeline = EmbeddingPipeline(...)

```python
pipeline = EmbeddingPipeline(config)
```

### Step 4: Assign embeddings = value

```python
embeddings = [[0.1] * 64, [0.2] * 128]
```

### Step 5: Assign is_valid = pipeline.validate_dimensions(...)

```python
is_valid = pipeline.validate_dimensions(embeddings)
```

**Verification:**
```python
assert not is_valid
```


## Complete Example

```python
# Workflow
'Test dimension validation with invalid embeddings.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=128)
pipeline = EmbeddingPipeline(config)
embeddings = [[0.1] * 64, [0.2] * 128]
is_valid = pipeline.validate_dimensions(embeddings)
assert not is_valid
```

## Next Steps


---

*Source: test_embedding_pipeline.py:207 | Complexity: Intermediate | Last updated: 2026-02-14*