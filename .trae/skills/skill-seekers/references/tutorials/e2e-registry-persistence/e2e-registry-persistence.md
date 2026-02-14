# How To: E2E Registry Persistence

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 9: Registry persistence across instances

Steps:
1. Add source with one SourceManager instance
2. Create new SourceManager instance
3. Verify source persists
4. Modify source with new instance
5. Verify changes persist

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

### Step 1: '\n        E2E Test 9: Registry persistence across instances\n\n        Steps:\n        1. Add source with one SourceManager instance\n        2. Create new SourceManager instance\n        3. Verify source persists\n        4. Modify source with new instance\n        5. Verify changes persist\n        '

```python
'\n        E2E Test 9: Registry persistence across instances\n\n        Steps:\n        1. Add source with one SourceManager instance\n        2. Create new SourceManager instance\n        3. Verify source persists\n        4. Modify source with new instance\n        5. Verify changes persist\n        '
```

**Verification:**
```python
assert len(sources) == 1
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert sources[0]['name'] == 'persistent-source'
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert sources[0]['priority'] == 25
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

**Verification:**
```python
assert source['priority'] == 50
```

### Step 5: Assign manager1 = SourceManager(...)

```python
manager1 = SourceManager(config_dir=config_dir)
```

### Step 6: Call manager1.add_source()

```python
manager1.add_source(name='persistent-source', git_url=git_url, priority=25)
```

### Step 7: Assign manager2 = SourceManager(...)

```python
manager2 = SourceManager(config_dir=config_dir)
```

### Step 8: Assign sources = manager2.list_sources(...)

```python
sources = manager2.list_sources()
```

**Verification:**
```python
assert len(sources) == 1
```

### Step 9: Call manager2.add_source()

```python
manager2.add_source(name='persistent-source', git_url=git_url, priority=50)
```

### Step 10: Assign manager3 = SourceManager(...)

```python
manager3 = SourceManager(config_dir=config_dir)
```

### Step 11: Assign source = manager3.get_source(...)

```python
source = manager3.get_source('persistent-source')
```

**Verification:**
```python
assert source['priority'] == 50
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 9: Registry persistence across instances\n\n        Steps:\n        1. Add source with one SourceManager instance\n        2. Create new SourceManager instance\n        3. Verify source persists\n        4. Modify source with new instance\n        5. Verify changes persist\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
manager1 = SourceManager(config_dir=config_dir)
manager1.add_source(name='persistent-source', git_url=git_url, priority=25)
manager2 = SourceManager(config_dir=config_dir)
sources = manager2.list_sources()
assert len(sources) == 1
assert sources[0]['name'] == 'persistent-source'
assert sources[0]['priority'] == 25
manager2.add_source(name='persistent-source', git_url=git_url, priority=50)
manager3 = SourceManager(config_dir=config_dir)
source = manager3.get_source('persistent-source')
assert source['priority'] == 50
```

## Next Steps


---

*Source: test_git_sources_e2e.py:444 | Complexity: Advanced | Last updated: 2026-02-14*