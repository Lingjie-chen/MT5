# How To: Chunking Preserves Small Docs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that small documents are not chunked.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `json`
- `pathlib`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.package_skill`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test that small documents are not chunked.'

```python
'Test that small documents are not chunked.'
```

**Verification:**
```python
assert len(data) == 2, 'Small docs should not be chunked'
```

### Step 2: Assign skill_dir = create_test_skill(...)

```python
skill_dir = create_test_skill(tmp_path, large_doc=False)
```

**Verification:**
```python
assert 'is_chunked' not in doc['metadata']
```

### Step 3: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('langchain')
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
```

**Verification:**
```python
assert len(data) == 2, 'Small docs should not be chunked'
```

### Step 5: Assign data = json.load(...)

```python
data = json.load(f)
```

**Verification:**
```python
assert 'is_chunked' not in doc['metadata']
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that small documents are not chunked.'
skill_dir = create_test_skill(tmp_path, large_doc=False)
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
with open(package_path) as f:
    data = json.load(f)
assert len(data) == 2, 'Small docs should not be chunked'
for doc in data:
    assert 'is_chunked' not in doc['metadata']
```

## Next Steps


---

*Source: test_chunking_integration.py:106 | Complexity: Intermediate | Last updated: 2026-02-14*