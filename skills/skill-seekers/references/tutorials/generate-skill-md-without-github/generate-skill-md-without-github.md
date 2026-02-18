# How To: Generate Skill Md Without Github

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test SKILL.md generation without GitHub (backward compat).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test SKILL.md generation without GitHub (backward compat).'

```python
'Test SKILL.md generation without GitHub (backward compat).'
```

**Verification:**
```python
assert '⭐' not in skill_md
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
```

**Verification:**
```python
assert 'Repository Info' not in skill_md
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert 'Quick Start (from README)' not in skill_md
```

### Step 4: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)])
```

**Verification:**
```python
assert 'Common Issues (from GitHub)' not in skill_md
```

### Step 5: Assign skill_md = generator.generate_skill_md(...)

```python
skill_md = generator.generate_skill_md()
```

**Verification:**
```python
assert 'When to Use This Skill' in skill_md
```

### Step 6: Call json.dump()

```python
json.dump(config, f)
```

**Verification:**
```python
assert 'How It Works' in skill_md
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test SKILL.md generation without GitHub (backward compat).'
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
skill_md = generator.generate_skill_md()
assert '⭐' not in skill_md
assert 'Repository Info' not in skill_md
assert 'Quick Start (from README)' not in skill_md
assert 'Common Issues (from GitHub)' not in skill_md
assert 'When to Use This Skill' in skill_md
assert 'How It Works' in skill_md
```

## Next Steps


---

*Source: test_generate_router_github.py:244 | Complexity: Intermediate | Last updated: 2026-02-14*