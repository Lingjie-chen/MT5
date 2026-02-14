# How To: Scenario 3 Router Without Github

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test router generation without GitHub data.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
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

### Step 1: 'Test router generation without GitHub data.'

```python
'Test router generation without GitHub data.'
```

**Verification:**
```python
assert 'internal-tool' in skill_md.lower()
```

### Step 2: Assign config1 = value

```python
config1 = tmp_path / 'internal-database.json'
```

**Verification:**
```python
assert 'Repository:' not in skill_md
```

### Step 3: Call config1.write_text()

```python
config1.write_text(json.dumps({'name': 'internal-database', 'description': 'Database layer', 'categories': {'database': ['db', 'sql', 'connection']}}))
```

**Verification:**
```python
assert 'Stars:' not in skill_md
```

### Step 4: Assign config2 = value

```python
config2 = tmp_path / 'internal-api.json'
```

**Verification:**
```python
assert '⭐' not in skill_md
```

### Step 5: Call config2.write_text()

```python
config2.write_text(json.dumps({'name': 'internal-api', 'description': 'API endpoints', 'categories': {'api': ['api', 'endpoint', 'route']}}))
```

**Verification:**
```python
assert 'Common Issues' not in skill_md
```

### Step 6: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator(config_paths=[str(config1), str(config2)], router_name='internal-tool', github_streams=None)
```

**Verification:**
```python
assert 'Issue #' not in skill_md
```

### Step 7: Assign skill_md = generator.generate_skill_md(...)

```python
skill_md = generator.generate_skill_md()
```

**Verification:**
```python
assert 'internal-database' in skill_md
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test router generation without GitHub data.'
config1 = tmp_path / 'internal-database.json'
config1.write_text(json.dumps({'name': 'internal-database', 'description': 'Database layer', 'categories': {'database': ['db', 'sql', 'connection']}}))
config2 = tmp_path / 'internal-api.json'
config2.write_text(json.dumps({'name': 'internal-api', 'description': 'API endpoints', 'categories': {'api': ['api', 'endpoint', 'route']}}))
generator = RouterGenerator(config_paths=[str(config1), str(config2)], router_name='internal-tool', github_streams=None)
skill_md = generator.generate_skill_md()
assert 'internal-tool' in skill_md.lower()
assert 'Repository:' not in skill_md
assert 'Stars:' not in skill_md
assert '⭐' not in skill_md
assert 'Common Issues' not in skill_md
assert 'Issue #' not in skill_md
assert 'internal-database' in skill_md
assert 'internal-api' in skill_md
```

## Next Steps


---

*Source: test_architecture_scenarios.py:778 | Complexity: Intermediate | Last updated: 2026-02-14*