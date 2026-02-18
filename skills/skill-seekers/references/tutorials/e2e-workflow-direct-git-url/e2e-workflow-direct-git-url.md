# How To: E2E Workflow Direct Git Url

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 1: Direct git URL workflow (no source registration)

Steps:
1. Clone repository via direct git URL
2. List available configs
3. Fetch specific config
4. Verify config content

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

### Step 1: '\n        E2E Test 1: Direct git URL workflow (no source registration)\n\n        Steps:\n        1. Clone repository via direct git URL\n        2. List available configs\n        3. Fetch specific config\n        4. Verify config content\n        '

```python
'\n        E2E Test 1: Direct git URL workflow (no source registration)\n\n        Steps:\n        1. Clone repository via direct git URL\n        2. List available configs\n        3. Fetch specific config\n        4. Verify config content\n        '
```

**Verification:**
```python
assert repo_path.exists()
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert (repo_path / '.git').exists()
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

**Verification:**
```python
assert set(config_names) == {'react', 'vue', 'django'}
```

### Step 5: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

**Verification:**
```python
assert config['name'] == 'react'
```

### Step 6: Assign repo_path = git_repo.clone_or_pull(...)

```python
repo_path = git_repo.clone_or_pull(source_name='test-direct', git_url=git_url, branch='master')
```

**Verification:**
```python
assert config['description'] == 'React framework for UIs'
```

### Step 7: Assign configs = git_repo.find_configs(...)

```python
configs = git_repo.find_configs(repo_path)
```

**Verification:**
```python
assert config['base_url'] == 'https://react.dev/'
```

### Step 8: Assign config_names = value

```python
config_names = [c.stem for c in configs]
```

**Verification:**
```python
assert 'selectors' in config
```

### Step 9: Assign config = git_repo.get_config(...)

```python
config = git_repo.get_config(repo_path, 'react')
```

**Verification:**
```python
assert 'categories' in config
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 1: Direct git URL workflow (no source registration)\n\n        Steps:\n        1. Clone repository via direct git URL\n        2. List available configs\n        3. Fetch specific config\n        4. Verify config content\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-direct', git_url=git_url, branch='master')
assert repo_path.exists()
assert (repo_path / '.git').exists()
configs = git_repo.find_configs(repo_path)
assert len(configs) == 3
config_names = [c.stem for c in configs]
assert set(config_names) == {'react', 'vue', 'django'}
config = git_repo.get_config(repo_path, 'react')
assert config['name'] == 'react'
assert config['description'] == 'React framework for UIs'
assert config['base_url'] == 'https://react.dev/'
assert 'selectors' in config
assert 'categories' in config
assert config['max_pages'] == 100
```

## Next Steps


---

*Source: test_git_sources_e2e.py:107 | Complexity: Advanced | Last updated: 2026-02-14*