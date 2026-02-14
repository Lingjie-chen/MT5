# How To: Get Config In Subdir

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test loading config from subdirectory.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `git.exc`
- `skill_seekers.mcp.git_repo`

**Setup Required:**
```python
# Fixtures: git_repo, temp_cache_dir
```

## Step-by-Step Guide

### Step 1: 'Test loading config from subdirectory.'

```python
'Test loading config from subdirectory.'
```

**Verification:**
```python
assert result == config_data
```

### Step 2: Assign repo_path = value

```python
repo_path = temp_cache_dir / 'test-repo'
```

### Step 3: Assign configs_dir = value

```python
configs_dir = repo_path / 'configs'
```

### Step 4: Call configs_dir.mkdir()

```python
configs_dir.mkdir(parents=True)
```

### Step 5: Assign config_data = value

```python
config_data = {'name': 'nestjs'}
```

### Step 6: Call unknown.write_text()

```python
(configs_dir / 'nestjs.json').write_text(json.dumps(config_data))
```

### Step 7: Assign result = git_repo.get_config(...)

```python
result = git_repo.get_config(repo_path, 'nestjs')
```

**Verification:**
```python
assert result == config_data
```


## Complete Example

```python
# Setup
# Fixtures: git_repo, temp_cache_dir

# Workflow
'Test loading config from subdirectory.'
repo_path = temp_cache_dir / 'test-repo'
configs_dir = repo_path / 'configs'
configs_dir.mkdir(parents=True)
config_data = {'name': 'nestjs'}
(configs_dir / 'nestjs.json').write_text(json.dumps(config_data))
result = git_repo.get_config(repo_path, 'nestjs')
assert result == config_data
```

## Next Steps


---

*Source: test_git_repo.py:370 | Complexity: Intermediate | Last updated: 2026-02-14*