# How To: Chroma Upload Without Chromadb Installed

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test upload fails gracefully without chromadb installed.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pytest`
- `skill_seekers.cli.adaptors`
- `sys`
- `sys`
- `skill_seekers.cli.upload_skill`
- `inspect`

**Setup Required:**
```python
# Fixtures: sample_chroma_package
```

## Step-by-Step Guide

### Step 1: 'Test upload fails gracefully without chromadb installed.'

```python
'Test upload fails gracefully without chromadb installed.'
```

**Verification:**
```python
assert result['success'] is False
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('chroma')
```

**Verification:**
```python
assert 'chromadb not installed' in result['message']
```

### Step 3: Assign chromadb_backup = sys.modules.get(...)

```python
chromadb_backup = sys.modules.get('chromadb')
```

**Verification:**
```python
assert 'pip install chromadb' in result['message']
```

### Step 4: Assign result = adaptor.upload(...)

```python
result = adaptor.upload(sample_chroma_package)
```

**Verification:**
```python
assert result['success'] is False
```

### Step 5: Assign unknown = chromadb_backup

```python
sys.modules['chromadb'] = chromadb_backup
```


## Complete Example

```python
# Setup
# Fixtures: sample_chroma_package

# Workflow
'Test upload fails gracefully without chromadb installed.'
adaptor = get_adaptor('chroma')
import sys
chromadb_backup = sys.modules.get('chromadb')
if 'chromadb' in sys.modules:
    del sys.modules['chromadb']
try:
    result = adaptor.upload(sample_chroma_package)
    assert result['success'] is False
    assert 'chromadb not installed' in result['message']
    assert 'pip install chromadb' in result['message']
finally:
    if chromadb_backup:
        sys.modules['chromadb'] = chromadb_backup
```

## Next Steps


---

*Source: test_upload_integration.py:79 | Complexity: Advanced | Last updated: 2026-02-14*