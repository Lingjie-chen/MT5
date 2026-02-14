# How To: E2E Source Name Validation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 8: Error handling - invalid source names

Steps:
1. Try to add sources with invalid names
2. Verify validation errors

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

### Step 1: '\n        E2E Test 8: Error handling - invalid source names\n\n        Steps:\n        1. Try to add sources with invalid names\n        2. Verify validation errors\n        '

```python
'\n        E2E Test 8: Error handling - invalid source names\n\n        Steps:\n        1. Try to add sources with invalid names\n        2. Verify validation errors\n        '
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

### Step 3: Assign source_manager = SourceManager(...)

```python
source_manager = SourceManager(config_dir=config_dir)
```

### Step 4: Assign invalid_names = value

```python
invalid_names = ['', 'name with spaces', 'name/with/slashes', 'name@with@symbols', 'name.with.dots', '123-only-numbers-start-is-ok', 'name!exclamation']
```

### Step 5: Assign valid_git_url = 'https://github.com/test/repo.git'

```python
valid_git_url = 'https://github.com/test/repo.git'
```

### Step 6: Call source_manager.add_source()

```python
source_manager.add_source(name=invalid_name, git_url=valid_git_url)
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs

# Workflow
'\n        E2E Test 8: Error handling - invalid source names\n\n        Steps:\n        1. Try to add sources with invalid names\n        2. Verify validation errors\n        '
cache_dir, config_dir = temp_dirs
source_manager = SourceManager(config_dir=config_dir)
invalid_names = ['', 'name with spaces', 'name/with/slashes', 'name@with@symbols', 'name.with.dots', '123-only-numbers-start-is-ok', 'name!exclamation']
valid_git_url = 'https://github.com/test/repo.git'
for invalid_name in invalid_names[:-2]:
    if invalid_name == '123-only-numbers-start-is-ok':
        continue
    with pytest.raises(ValueError, match='Invalid source name'):
        source_manager.add_source(name=invalid_name, git_url=valid_git_url)
```

## Next Steps


---

*Source: test_git_sources_e2e.py:414 | Complexity: Intermediate | Last updated: 2026-02-14*