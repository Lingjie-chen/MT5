# How To: Router Without Github Streams

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that router generation works without GitHub streams (backward compat).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test that router generation works without GitHub streams (backward compat).'

```python
'Test that router generation works without GitHub streams (backward compat).'
```

**Verification:**
```python
assert generator.github_metadata is None
```

### Step 2: Assign config = value

```python
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://example.com', 'categories': {'api': ['api']}}
```

**Verification:**
```python
assert generator.github_docs is None
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert generator.github_issues is None
```

### Step 4: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)])
```

**Verification:**
```python
assert 'When to Use This Skill' in skill_md
```

### Step 5: Assign skill_md = generator.generate_skill_md(...)

```python
skill_md = generator.generate_skill_md()
```

**Verification:**
```python
assert 'How It Works' in skill_md
```

### Step 6: Call json.dump()

```python
json.dump(config, f)
```

**Verification:**
```python
assert '⭐' not in skill_md
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that router generation works without GitHub streams (backward compat).'
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://example.com', 'categories': {'api': ['api']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
assert generator.github_metadata is None
assert generator.github_docs is None
assert generator.github_issues is None
skill_md = generator.generate_skill_md()
assert 'When to Use This Skill' in skill_md
assert 'How It Works' in skill_md
assert '⭐' not in skill_md
assert 'Repository Info' not in skill_md
assert 'Quick Start (from README)' not in skill_md
assert 'Common Issues (from GitHub)' not in skill_md
```

## Next Steps


---

*Source: test_e2e_three_stream_pipeline.py:504 | Complexity: Intermediate | Last updated: 2026-02-14*