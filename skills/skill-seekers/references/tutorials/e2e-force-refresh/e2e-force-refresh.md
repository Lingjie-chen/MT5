# How To: E2E Force Refresh

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 5: Force refresh (delete and re-clone)

Steps:
1. Clone repository
2. Modify local cache manually
3. Force refresh
4. Verify cache was reset

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

### Step 1: '\n        E2E Test 5: Force refresh (delete and re-clone)\n\n        Steps:\n        1. Clone repository\n        2. Modify local cache manually\n        3. Force refresh\n        4. Verify cache was reset\n        '

```python
'\n        E2E Test 5: Force refresh (delete and re-clone)\n\n        Steps:\n        1. Clone repository\n        2. Modify local cache manually\n        3. Force refresh\n        4. Verify cache was reset\n        '
```

**Verification:**
```python
assert corrupt_file.exists()
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert not corrupt_file.exists()
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert len(configs) == 3
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

### Step 5: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

### Step 6: Assign repo_path = git_repo.clone_or_pull(...)

```python
repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master')
```

### Step 7: Assign corrupt_file = value

```python
corrupt_file = repo_path / 'CORRUPTED.txt'
```

**Verification:**
```python
assert corrupt_file.exists()
```

### Step 8: Assign refreshed_repo_path = git_repo.clone_or_pull(...)

```python
refreshed_repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master', force_refresh=True)
```

**Verification:**
```python
assert not corrupt_file.exists()
```

### Step 9: Assign configs = git_repo.find_configs(...)

```python
configs = git_repo.find_configs(refreshed_repo_path)
```

**Verification:**
```python
assert len(configs) == 3
```

### Step 10: Call f.write()

```python
f.write('This file should not exist after refresh')
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 5: Force refresh (delete and re-clone)\n\n        Steps:\n        1. Clone repository\n        2. Modify local cache manually\n        3. Force refresh\n        4. Verify cache was reset\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master')
corrupt_file = repo_path / 'CORRUPTED.txt'
with open(corrupt_file, 'w') as f:
    f.write('This file should not exist after refresh')
assert corrupt_file.exists()
refreshed_repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master', force_refresh=True)
assert not corrupt_file.exists()
configs = git_repo.find_configs(refreshed_repo_path)
assert len(configs) == 3
```

## Next Steps


---

*Source: test_git_sources_e2e.py:321 | Complexity: Advanced | Last updated: 2026-02-14*