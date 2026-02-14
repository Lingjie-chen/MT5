# How To: Weaviate Upload Without Weaviate Installed

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test upload fails gracefully without weaviate-client installed.

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
# Fixtures: sample_weaviate_package
```

## Step-by-Step Guide

### Step 1: 'Test upload fails gracefully without weaviate-client installed.'

```python
'Test upload fails gracefully without weaviate-client installed.'
```

**Verification:**
```python
assert result['success'] is False
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('weaviate')
```

**Verification:**
```python
assert 'weaviate-client not installed' in result['message']
```

### Step 3: Assign weaviate_backup = sys.modules.get(...)

```python
weaviate_backup = sys.modules.get('weaviate')
```

**Verification:**
```python
assert 'pip install weaviate-client' in result['message']
```

### Step 4: Assign result = adaptor.upload(...)

```python
result = adaptor.upload(sample_weaviate_package)
```

**Verification:**
```python
assert result['success'] is False
```

### Step 5: Assign unknown = weaviate_backup

```python
sys.modules['weaviate'] = weaviate_backup
```


## Complete Example

```python
# Setup
# Fixtures: sample_weaviate_package

# Workflow
'Test upload fails gracefully without weaviate-client installed.'
adaptor = get_adaptor('weaviate')
import sys
weaviate_backup = sys.modules.get('weaviate')
if 'weaviate' in sys.modules:
    del sys.modules['weaviate']
try:
    result = adaptor.upload(sample_weaviate_package)
    assert result['success'] is False
    assert 'weaviate-client not installed' in result['message']
    assert 'pip install weaviate-client' in result['message']
finally:
    if weaviate_backup:
        sys.modules['weaviate'] = weaviate_backup
```

## Next Steps


---

*Source: test_upload_integration.py:121 | Complexity: Advanced | Last updated: 2026-02-14*