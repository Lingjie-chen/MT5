# How To: Local Provider Deterministic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test local provider generates deterministic embeddings.

## Prerequisites

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.embedding_pipeline`


## Step-by-Step Guide

### Step 1: 'Test local provider generates deterministic embeddings.'

```python
'Test local provider generates deterministic embeddings.'
```

**Verification:**
```python
assert emb1 == emb2
```

### Step 2: Assign provider = LocalEmbeddingProvider(...)

```python
provider = LocalEmbeddingProvider(dimension=64)
```

### Step 3: Assign text = 'same text'

```python
text = 'same text'
```

### Step 4: Assign emb1 = value

```python
emb1 = provider.generate_embeddings([text])[0]
```

### Step 5: Assign emb2 = value

```python
emb2 = provider.generate_embeddings([text])[0]
```

**Verification:**
```python
assert emb1 == emb2
```


## Complete Example

```python
# Workflow
'Test local provider generates deterministic embeddings.'
provider = LocalEmbeddingProvider(dimension=64)
text = 'same text'
emb1 = provider.generate_embeddings([text])[0]
emb2 = provider.generate_embeddings([text])[0]
assert emb1 == emb2
```

## Next Steps


---

*Source: test_embedding_pipeline.py:45 | Complexity: Intermediate | Last updated: 2026-02-14*