# How To: E2E Config Not Found

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 6: Error handling - config not found

Steps:
1. Clone repository
2. Try to fetch non-existent config
3. Verify helpful error message with suggestions

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `pathlib`
- `git`
- `pytest`
- `skill_seekers.mcp.git_repo`
- `skill_seekers.mcp.source_manager`
- `mcp`
- `mcp.types`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`

**Setup Required:**
```python
# Fixtures: temp_dirs, temp_git_repo
```

## Step-by-Step Guide

### Step 1: '\n        E2E Test 6: Error handling - config not found\n\n        Steps:\n        1. Clone repository\n        2. Try to fetch non-existent config\n        3. Verify helpful error message with suggestions\n        '

```python
'\n        E2E Test 6: Error handling - config not found\n\n        Steps:\n        1. Clone repository\n        2. Try to fetch non-existent config\n        3. Verify helpful error message with suggestions\n        '
```

**Verification:**
```python
assert 'nonexistent.json' in error_msg
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert 'not found' in error_msg
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert 'react' in error_msg
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

**Verification:**
```python
assert 'vue' in error_msg
```

### Step 5: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

**Verification:**
```python
assert 'django' in error_msg
```

### Step 6: Assign repo_path = git_repo.clone_or_pull(...)

```python
repo_path = git_repo.clone_or_pull(source_name='test-not-found', git_url=git_url, branch='master')
```

### Step 7: Assign error_msg = str(...)

```python
error_msg = str(exc_info.value)
```

**Verification:**
```python
assert 'nonexistent.json' in error_msg
```

### Step 8: Call git_repo.get_config()

```python
git_repo.get_config(repo_path, 'nonexistent')
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 6: Error handling - config not found\n\n        Steps:\n        1. Clone repository\n        2. Try to fetch non-existent config\n        3. Verify helpful error message with suggestions\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-not-found', git_url=git_url, branch='master')
with pytest.raises(FileNotFoundError) as exc_info:
    git_repo.get_config(repo_path, 'nonexistent')
error_msg = str(exc_info.value)
assert 'nonexistent.json' in error_msg
assert 'not found' in error_msg
assert 'react' in error_msg
assert 'vue' in error_msg
assert 'django' in error_msg
```

## Next Steps


---

*Source: test_git_sources_e2e.py:362 | Complexity: Advanced | Last updated: 2026-02-14*