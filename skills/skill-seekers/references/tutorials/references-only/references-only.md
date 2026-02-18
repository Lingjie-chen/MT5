# How To: References Only

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test skill with references but no SKILL.md.

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

### Step 1: 'Test skill with references but no SKILL.md.'

```python
'Test skill with references but no SKILL.md.'
```

**Verification:**
```python
assert len(result['points']) == 1
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'refs_only'
```

**Verification:**
```python
assert result['points'][0]['payload']['category'] == 'test'
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert result['points'][0]['payload']['type'] == 'reference'
```

### Step 4: Assign refs_dir = value

```python
refs_dir = skill_dir / 'references'
```

### Step 5: Call refs_dir.mkdir()

```python
refs_dir.mkdir()
```

### Step 6: Call unknown.write_text()

```python
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
```

### Step 7: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('qdrant')
```

### Step 8: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
```

### Step 9: Assign points_json = adaptor.format_skill_md(...)

```python
points_json = adaptor.format_skill_md(skill_dir, metadata)
```

### Step 10: Assign result = json.loads(...)

```python
result = json.loads(points_json)
```

**Verification:**
```python
assert len(result['points']) == 1
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert len(result['points']) == 1
assert result['points'][0]['payload']['category'] == 'test'
assert result['points'][0]['payload']['type'] == 'reference'
```

## Next Steps


---

*Source: test_qdrant_adaptor.py:168 | Complexity: Advanced | Last updated: 2026-02-14*