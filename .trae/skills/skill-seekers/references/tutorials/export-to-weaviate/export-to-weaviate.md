# How To: Export To Weaviate

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Weaviate export tool.

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

### Step 1: 'Test Weaviate export tool.'

```python
'Test Weaviate export tool.'
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
assert len(result) == 1
```

### Step 3: Assign args = value

```python
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
```

**Verification:**
```python
assert hasattr(result[0], 'text')
```

### Step 4: Assign result = run_async(...)

```python
result = run_async(export_to_weaviate_impl(args))
```

**Verification:**
```python
assert '✅ Weaviate Export Complete!' in text
```

### Step 5: Assign text = value

```python
text = result[0].text
```

**Verification:**
```python
assert 'test_skill-weaviate.json' in text
```


## Complete Example

```python
# Setup
# Fixtures: test_skill_dir

# Workflow
'Test Weaviate export tool.'
output_dir = test_skill_dir.parent
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
result = run_async(export_to_weaviate_impl(args))
assert isinstance(result, list)
assert len(result) == 1
assert hasattr(result[0], 'text')
text = result[0].text
assert '✅ Weaviate Export Complete!' in text
assert 'test_skill-weaviate.json' in text
assert 'weaviate.Client' in text
```

## Next Steps


---

*Source: test_mcp_vector_dbs.py:60 | Complexity: Advanced | Last updated: 2026-02-14*