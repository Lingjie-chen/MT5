# How To: All Exports Create Files

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that all export tools create output files.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `json`
- `asyncio`
- `skill_seekers.mcp.tools.vector_db_tools`

**Setup Required:**
```python
# Fixtures: test_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Test that all export tools create output files.'

```python
'Test that all export tools create output files.'
```

**Verification:**
```python
assert isinstance(result, list)
```

### Step 2: Assign output_dir = value

```python
output_dir = test_skill_dir.parent
```

**Verification:**
```python
assert '✅' in text
```

### Step 3: Assign exports = value

```python
exports = [('weaviate', export_to_weaviate_impl), ('chroma', export_to_chroma_impl), ('faiss', export_to_faiss_impl), ('qdrant', export_to_qdrant_impl)]
```

**Verification:**
```python
assert expected_file.exists(), f'{target} export file not created'
```

### Step 4: Assign args = value

```python
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
```

**Verification:**
```python
assert isinstance(data, dict)
```

### Step 5: Assign result = run_async(...)

```python
result = run_async(export_func(args))
```

**Verification:**
```python
assert isinstance(result, list)
```

### Step 6: Assign text = value

```python
text = result[0].text
```

**Verification:**
```python
assert '✅' in text
```

### Step 7: Assign expected_file = value

```python
expected_file = output_dir / f'test_skill-{target}.json'
```

**Verification:**
```python
assert expected_file.exists(), f'{target} export file not created'
```

### Step 8: Assign data = json.load(...)

```python
data = json.load(f)
```

**Verification:**
```python
assert isinstance(data, dict)
```


## Complete Example

```python
# Setup
# Fixtures: test_skill_dir

# Workflow
'Test that all export tools create output files.'
output_dir = test_skill_dir.parent
exports = [('weaviate', export_to_weaviate_impl), ('chroma', export_to_chroma_impl), ('faiss', export_to_faiss_impl), ('qdrant', export_to_qdrant_impl)]
for target, export_func in exports:
    args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
    result = run_async(export_func(args))
    assert isinstance(result, list)
    text = result[0].text
    assert '✅' in text
    expected_file = output_dir / f'test_skill-{target}.json'
    assert expected_file.exists(), f'{target} export file not created'
    with open(expected_file) as f:
        data = json.load(f)
        assert isinstance(data, dict)
```

## Next Steps


---

*Source: test_mcp_vector_dbs.py:179 | Complexity: Advanced | Last updated: 2026-02-14*