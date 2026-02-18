# How To: Format Skill Md

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test formatting SKILL.md as Qdrant points.

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

### Step 1: 'Test formatting SKILL.md as Qdrant points.'

```python
'Test formatting SKILL.md as Qdrant points.'
```

**Verification:**
```python
assert 'collection_name' in result
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'test_skill'
```

**Verification:**
```python
assert 'points' in result
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert 'config' in result
```

### Step 4: Assign skill_md = value

```python
skill_md = skill_dir / 'SKILL.md'
```

**Verification:**
```python
assert len(result['points']) == 3
```

### Step 5: Call skill_md.write_text()

```python
skill_md.write_text('# Test Skill\n\nThis is a test skill for Qdrant format.')
```

**Verification:**
```python
assert 'id' in point
```

### Step 6: Assign refs_dir = value

```python
refs_dir = skill_dir / 'references'
```

**Verification:**
```python
assert 'vector' in point
```

### Step 7: Call refs_dir.mkdir()

```python
refs_dir.mkdir()
```

**Verification:**
```python
assert 'payload' in point
```

### Step 8: Call unknown.write_text()

```python
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
```

**Verification:**
```python
assert 'content' in payload
```

### Step 9: Call unknown.write_text()

```python
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
```

**Verification:**
```python
assert payload['source'] == 'test_skill'
```

### Step 10: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('qdrant')
```

**Verification:**
```python
assert payload['version'] == '1.0.0'
```

### Step 11: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

**Verification:**
```python
assert 'category' in payload
```

### Step 12: Assign points_json = adaptor.format_skill_md(...)

```python
points_json = adaptor.format_skill_md(skill_dir, metadata)
```

**Verification:**
```python
assert 'file' in payload
```

### Step 13: Assign result = json.loads(...)

```python
result = json.loads(points_json)
```

**Verification:**
```python
assert 'type' in payload
```

### Step 14: Assign categories = value

```python
categories = {point['payload']['category'] for point in result['points']}
```

**Verification:**
```python
assert 'overview' in categories
```

### Step 15: Assign payload = value

```python
payload = point['payload']
```

**Verification:**
```python
assert 'getting started' in categories or 'api' in categories
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test formatting SKILL.md as Qdrant points.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for Qdrant format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert 'collection_name' in result
assert 'points' in result
assert 'config' in result
assert len(result['points']) == 3
for point in result['points']:
    assert 'id' in point
    assert 'vector' in point
    assert 'payload' in point
    payload = point['payload']
    assert 'content' in payload
    assert payload['source'] == 'test_skill'
    assert payload['version'] == '1.0.0'
    assert 'category' in payload
    assert 'file' in payload
    assert 'type' in payload
categories = {point['payload']['category'] for point in result['points']}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

## Next Steps


---

*Source: test_qdrant_adaptor.py:23 | Complexity: Advanced | Last updated: 2026-02-14*