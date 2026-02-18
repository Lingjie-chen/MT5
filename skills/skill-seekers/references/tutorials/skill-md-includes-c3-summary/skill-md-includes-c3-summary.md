# How To: Skill Md Includes C3 Summary

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test SKILL.md includes C3.x architecture summary.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.config_validator`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_skill_builder`

**Setup Required:**
```python
# Fixtures: mock_config, mock_c3_data, temp_dir
```

## Step-by-Step Guide

### Step 1: 'Test SKILL.md includes C3.x architecture summary.'

```python
'Test SKILL.md includes C3.x architecture summary.'
```

**Verification:**
```python
assert '## 🏗️ Architecture & Code Analysis' in content
```

### Step 2: Assign scraped_data = value

```python
scraped_data = {'github': {'data': {'readme': 'Test README', 'c3_analysis': mock_c3_data}}}
```

**Verification:**
```python
assert 'Primary Architecture' in content
```

### Step 3: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(mock_config, scraped_data)
```

**Verification:**
```python
assert 'MVC' in content
```

### Step 4: Assign builder.skill_dir = temp_dir

```python
builder.skill_dir = temp_dir
```

**Verification:**
```python
assert 'Design Patterns' in content
```

### Step 5: Call builder._generate_skill_md()

```python
builder._generate_skill_md()
```

**Verification:**
```python
assert 'Factory' in content
```

### Step 6: Assign skill_file = os.path.join(...)

```python
skill_file = os.path.join(temp_dir, 'SKILL.md')
```

**Verification:**
```python
assert 'references/codebase_analysis/ARCHITECTURE.md' in content
```

### Step 7: Assign content = f.read(...)

```python
content = f.read()
```


## Complete Example

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

# Workflow
'Test SKILL.md includes C3.x architecture summary.'
scraped_data = {'github': {'data': {'readme': 'Test README', 'c3_analysis': mock_c3_data}}}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
builder._generate_skill_md()
skill_file = os.path.join(temp_dir, 'SKILL.md')
with open(skill_file) as f:
    content = f.read()
assert '## 🏗️ Architecture & Code Analysis' in content
assert 'Primary Architecture' in content
assert 'MVC' in content
assert 'Design Patterns' in content
assert 'Factory' in content
assert 'references/codebase_analysis/ARCHITECTURE.md' in content
```

## Next Steps


---

*Source: test_c3_integration.py:339 | Complexity: Intermediate | Last updated: 2026-02-14*