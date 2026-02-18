# How To: E2E Pull Existing Repository

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 4: Pull updates from existing repository

Steps:
1. Clone repository
2. Add new commit to original repo
3. Pull updates
4. Verify new config is available

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

### Step 1: '\n        E2E Test 4: Pull updates from existing repository\n\n        Steps:\n        1. Clone repository\n        2. Add new commit to original repo\n        3. Pull updates\n        4. Verify new config is available\n        '

```python
'\n        E2E Test 4: Pull updates from existing repository\n\n        Steps:\n        1. Clone repository\n        2. Add new commit to original repo\n        3. Pull updates\n        4. Verify new config is available\n        '
```

**Verification:**
```python
assert len(initial_configs) == 3
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert len(updated_configs) == 4
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert fastapi_config['name'] == 'fastapi'
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

**Verification:**
```python
assert fastapi_config['max_pages'] == 150
```

### Step 5: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

### Step 6: Assign repo_path = git_repo.clone_or_pull(...)

```python
repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master')
```

### Step 7: Assign initial_configs = git_repo.find_configs(...)

```python
initial_configs = git_repo.find_configs(repo_path)
```

**Verification:**
```python
assert len(initial_configs) == 3
```

### Step 8: Assign new_config = value

```python
new_config = {'name': 'fastapi', 'description': 'FastAPI framework', 'base_url': 'https://fastapi.tiangolo.com/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 150}
```

### Step 9: Assign new_config_path = value

```python
new_config_path = Path(repo_dir) / 'fastapi.json'
```

### Step 10: Call repo.index.add()

```python
repo.index.add(['fastapi.json'])
```

### Step 11: Call repo.index.commit()

```python
repo.index.commit('Add FastAPI config')
```

### Step 12: Assign updated_repo_path = git_repo.clone_or_pull(...)

```python
updated_repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master', force_refresh=False)
```

### Step 13: Assign updated_configs = git_repo.find_configs(...)

```python
updated_configs = git_repo.find_configs(updated_repo_path)
```

**Verification:**
```python
assert len(updated_configs) == 4
```

### Step 14: Assign fastapi_config = git_repo.get_config(...)

```python
fastapi_config = git_repo.get_config(updated_repo_path, 'fastapi')
```

**Verification:**
```python
assert fastapi_config['name'] == 'fastapi'
```

### Step 15: Call json.dump()

```python
json.dump(new_config, f, indent=2)
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 4: Pull updates from existing repository\n\n        Steps:\n        1. Clone repository\n        2. Add new commit to original repo\n        3. Pull updates\n        4. Verify new config is available\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master')
initial_configs = git_repo.find_configs(repo_path)
assert len(initial_configs) == 3
new_config = {'name': 'fastapi', 'description': 'FastAPI framework', 'base_url': 'https://fastapi.tiangolo.com/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 150}
new_config_path = Path(repo_dir) / 'fastapi.json'
with open(new_config_path, 'w') as f:
    json.dump(new_config, f, indent=2)
repo.index.add(['fastapi.json'])
repo.index.commit('Add FastAPI config')
updated_repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master', force_refresh=False)
updated_configs = git_repo.find_configs(updated_repo_path)
assert len(updated_configs) == 4
fastapi_config = git_repo.get_config(updated_repo_path, 'fastapi')
assert fastapi_config['name'] == 'fastapi'
assert fastapi_config['max_pages'] == 150
```

## Next Steps


---

*Source: test_git_sources_e2e.py:262 | Complexity: Advanced | Last updated: 2026-02-14*