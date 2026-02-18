# How To: Langchain Chunking Enabled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that LangChain chunks large documents when enabled.

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

### Step 1: 'Test that LangChain chunks large documents when enabled.'

```python
'Test that LangChain chunks large documents when enabled.'
```

**Verification:**
```python
assert len(data) > 2, f'Large doc should be chunked, got {len(data)} docs'
```

### Step 2: Assign skill_dir = create_test_skill(...)

```python
skill_dir = create_test_skill(tmp_path, large_doc=True)
```

**Verification:**
```python
assert len(chunked_docs) > 0, 'Should have chunked documents'
```

### Step 3: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('langchain')
```

**Verification:**
```python
assert 'chunk_index' in doc['metadata']
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
```

**Verification:**
```python
assert 'total_chunks' in doc['metadata']
```

### Step 5: Assign chunked_docs = value

```python
chunked_docs = [doc for doc in data if doc['metadata'].get('is_chunked')]
```

**Verification:**
```python
assert 'chunk_id' in doc['metadata']
```

### Step 6: Assign data = json.load(...)

```python
data = json.load(f)
```

**Verification:**
```python
assert 'chunk_index' in doc['metadata']
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that LangChain chunks large documents when enabled.'
skill_dir = create_test_skill(tmp_path, large_doc=True)
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
with open(package_path) as f:
    data = json.load(f)
assert len(data) > 2, f'Large doc should be chunked, got {len(data)} docs'
chunked_docs = [doc for doc in data if doc['metadata'].get('is_chunked')]
assert len(chunked_docs) > 0, 'Should have chunked documents'
for doc in chunked_docs:
    assert 'chunk_index' in doc['metadata']
    assert 'total_chunks' in doc['metadata']
    assert 'chunk_id' in doc['metadata']
```

## Next Steps


---

*Source: test_chunking_integration.py:81 | Complexity: Intermediate | Last updated: 2026-02-14*