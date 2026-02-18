# How To: E2E Invalid Git Url

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 7: Error handling - invalid git URL

Steps:
1. Try to clone with invalid URL
2. Verify validation error

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
# Fixtures: temp_dirs
```

## Step-by-Step Guide

### Step 1: '\n        E2E Test 7: Error handling - invalid git URL\n\n        Steps:\n        1. Try to clone with invalid URL\n        2. Verify validation error\n        '

```python
'\n        E2E Test 7: Error handling - invalid git URL\n\n        Steps:\n        1. Try to clone with invalid URL\n        2. Verify validation error\n        '
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

### Step 3: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

### Step 4: Assign invalid_urls = value

```python
invalid_urls = ['', 'not-a-url', 'ftp://invalid.com/repo.git', "javascript:alert('xss')"]
```

### Step 5: Call git_repo.clone_or_pull()

```python
git_repo.clone_or_pull(source_name='test-invalid', git_url=invalid_url, branch='master')
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs

# Workflow
'\n        E2E Test 7: Error handling - invalid git URL\n\n        Steps:\n        1. Try to clone with invalid URL\n        2. Verify validation error\n        '
cache_dir, config_dir = temp_dirs
git_repo = GitConfigRepo(cache_dir=cache_dir)
invalid_urls = ['', 'not-a-url', 'ftp://invalid.com/repo.git', "javascript:alert('xss')"]
for invalid_url in invalid_urls:
    with pytest.raises(ValueError, match='Invalid git URL'):
        git_repo.clone_or_pull(source_name='test-invalid', git_url=invalid_url, branch='master')
```

## Next Steps


---

*Source: test_git_sources_e2e.py:394 | Complexity: Intermediate | Last updated: 2026-02-14*