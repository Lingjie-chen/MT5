# How To: Empty Skill Directory

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test handling of empty skill directory.

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

### Step 1: 'Test handling of empty skill directory.'

```python
'Test handling of empty skill directory.'
```

**Verification:**
```python
assert 'points' in result
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'empty_skill'
```

**Verification:**
```python
assert result['points'] == []
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

### Step 4: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('qdrant')
```

### Step 5: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
```

### Step 6: Assign points_json = adaptor.format_skill_md(...)

```python
points_json = adaptor.format_skill_md(skill_dir, metadata)
```

### Step 7: Assign result = json.loads(...)

```python
result = json.loads(points_json)
```

**Verification:**
```python
assert 'points' in result
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert 'points' in result
assert result['points'] == []
```

## Next Steps


---

*Source: test_qdrant_adaptor.py:153 | Complexity: Intermediate | Last updated: 2026-02-14*