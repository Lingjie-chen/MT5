# How To: Skill Builder Basic

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic skill building

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `tempfile`
- `pathlib`
- `pytest`
- `skill_seekers.cli.config_validator`
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_skill_builder`
- `json`
- `tempfile`


## Step-by-Step Guide

### Step 1: 'Test basic skill building'

```python
'Test basic skill building'
```

**Verification:**
```python
assert skill_md.exists()
```

### Step 2: Assign config = value

```python
config = {'name': 'test_skill', 'description': 'Test skill description', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
```

**Verification:**
```python
assert 'test_skill' in content.lower()
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': {'pages': [], 'data_file': '/tmp/test.json'}}
```

**Verification:**
```python
assert 'Test skill description' in content
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Assign builder.skill_dir = tmpdir

```python
builder.skill_dir = tmpdir
```

### Step 6: Call builder._generate_skill_md()

```python
builder._generate_skill_md()
```

### Step 7: Assign skill_md = value

```python
skill_md = Path(tmpdir) / 'SKILL.md'
```

**Verification:**
```python
assert skill_md.exists()
```

### Step 8: Assign content = skill_md.read_text(...)

```python
content = skill_md.read_text()
```

**Verification:**
```python
assert 'test_skill' in content.lower()
```


## Complete Example

```python
# Workflow
'Test basic skill building'
config = {'name': 'test_skill', 'description': 'Test skill description', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
scraped_data = {'documentation': {'pages': [], 'data_file': '/tmp/test.json'}}
with tempfile.TemporaryDirectory() as tmpdir:
    builder = UnifiedSkillBuilder(config, scraped_data)
    builder.skill_dir = tmpdir
    builder._generate_skill_md()
    skill_md = Path(tmpdir) / 'SKILL.md'
    assert skill_md.exists()
    content = skill_md.read_text()
    assert 'test_skill' in content.lower()
    assert 'Test skill description' in content
```

## Next Steps


---

*Source: test_unified.py:438 | Complexity: Advanced | Last updated: 2026-02-14*