# How To: Package Output Filename

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test package output filename generation.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pytest`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.adaptors.base`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test package output filename generation.'

```python
'Test package output filename generation.'
```

**Verification:**
```python
assert output_path.name == 'react-qdrant.json'
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'react'
```

**Verification:**
```python
assert output_path.suffix == '.json'
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert 'qdrant' in output_path.name
```

### Step 4: Call unknown.write_text()

```python
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
```

### Step 5: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('qdrant')
```

### Step 6: Assign output_path = adaptor.package(...)

```python
output_path = adaptor.package(skill_dir, tmp_path)
```

**Verification:**
```python
assert output_path.name == 'react-qdrant.json'
```

### Step 7: Assign output_path = adaptor.package(...)

```python
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
```

**Verification:**
```python
assert output_path.suffix == '.json'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('qdrant')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-qdrant.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'qdrant' in output_path.name
```

## Next Steps


---

*Source: test_qdrant_adaptor.py:97 | Complexity: Intermediate | Last updated: 2026-02-14*