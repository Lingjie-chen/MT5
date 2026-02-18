# How To: Cache Persistence

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test cache persistence to file.

## Prerequisites

**Required Modules:**
- `pytest`
- `tempfile`
- `pathlib`
- `unittest.mock`
- `skill_seekers.embedding.models`
- `skill_seekers.embedding.generator`
- `skill_seekers.embedding.cache`
- `numpy`


## Step-by-Step Guide

### Step 1: 'Test cache persistence to file.'

```python
'Test cache persistence to file.'
```

**Verification:**
```python
assert retrieved == [0.1, 0.2, 0.3]
```

### Step 2: Assign tmp_path = value

```python
tmp_path = tmp.name
```

### Step 3: Assign cache1 = EmbeddingCache(...)

```python
cache1 = EmbeddingCache(tmp_path)
```

### Step 4: Call cache1.set()

```python
cache1.set('hash1', [0.1, 0.2, 0.3], 'model1')
```

### Step 5: Call cache1.close()

```python
cache1.close()
```

### Step 6: Assign cache2 = EmbeddingCache(...)

```python
cache2 = EmbeddingCache(tmp_path)
```

### Step 7: Assign retrieved = cache2.get(...)

```python
retrieved = cache2.get('hash1')
```

**Verification:**
```python
assert retrieved == [0.1, 0.2, 0.3]
```

### Step 8: Call cache2.close()

```python
cache2.close()
```

### Step 9: Call Path.unlink()

```python
Path(tmp_path).unlink(missing_ok=True)
```


## Complete Example

```python
# Workflow
'Test cache persistence to file.'
with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
    tmp_path = tmp.name
try:
    cache1 = EmbeddingCache(tmp_path)
    cache1.set('hash1', [0.1, 0.2, 0.3], 'model1')
    cache1.close()
    cache2 = EmbeddingCache(tmp_path)
    retrieved = cache2.get('hash1')
    assert retrieved == [0.1, 0.2, 0.3]
    cache2.close()
finally:
    Path(tmp_path).unlink(missing_ok=True)
```

## Next Steps


---

*Source: test_embedding.py:349 | Complexity: Advanced | Last updated: 2026-02-14*