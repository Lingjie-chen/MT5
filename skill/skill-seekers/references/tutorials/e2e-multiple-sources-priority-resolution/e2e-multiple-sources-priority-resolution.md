# How To: E2E Multiple Sources Priority Resolution

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 3: Multiple sources with priority resolution

Steps:
1. Add multiple sources with different priorities
2. Verify sources are sorted by priority
3. Enable/disable sources
4. List enabled sources only

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

### Step 1: '\n        E2E Test 3: Multiple sources with priority resolution\n\n        Steps:\n        1. Add multiple sources with different priorities\n        2. Verify sources are sorted by priority\n        3. Enable/disable sources\n        4. List enabled sources only\n        '

```python
'\n        E2E Test 3: Multiple sources with priority resolution\n\n        Steps:\n        1. Add multiple sources with different priorities\n        2. Verify sources are sorted by priority\n        3. Enable/disable sources\n        4. List enabled sources only\n        '
```

**Verification:**
```python
assert len(sources) == 3
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert sources[0]['name'] == 'high-priority'
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert sources[1]['name'] == 'medium-priority'
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

**Verification:**
```python
assert sources[2]['name'] == 'low-priority'
```

### Step 5: Assign source_manager = SourceManager(...)

```python
source_manager = SourceManager(config_dir=config_dir)
```

**Verification:**
```python
assert len(enabled_sources) == 2
```

### Step 6: Call source_manager.add_source()

```python
source_manager.add_source(name='low-priority', git_url=git_url, priority=100)
```

**Verification:**
```python
assert all((s['enabled'] for s in enabled_sources))
```

### Step 7: Call source_manager.add_source()

```python
source_manager.add_source(name='high-priority', git_url=git_url, priority=1)
```

**Verification:**
```python
assert 'high-priority' not in [s['name'] for s in enabled_sources]
```

### Step 8: Call source_manager.add_source()

```python
source_manager.add_source(name='medium-priority', git_url=git_url, priority=50)
```

### Step 9: Assign sources = source_manager.list_sources(...)

```python
sources = source_manager.list_sources()
```

**Verification:**
```python
assert len(sources) == 3
```

### Step 10: Call source_manager.add_source()

```python
source_manager.add_source(name='high-priority', git_url=git_url, priority=1, enabled=False)
```

### Step 11: Assign enabled_sources = source_manager.list_sources(...)

```python
enabled_sources = source_manager.list_sources(enabled_only=True)
```

**Verification:**
```python
assert len(enabled_sources) == 2
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 3: Multiple sources with priority resolution\n\n        Steps:\n        1. Add multiple sources with different priorities\n        2. Verify sources are sorted by priority\n        3. Enable/disable sources\n        4. List enabled sources only\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
source_manager = SourceManager(config_dir=config_dir)
source_manager.add_source(name='low-priority', git_url=git_url, priority=100)
source_manager.add_source(name='high-priority', git_url=git_url, priority=1)
source_manager.add_source(name='medium-priority', git_url=git_url, priority=50)
sources = source_manager.list_sources()
assert len(sources) == 3
assert sources[0]['name'] == 'high-priority'
assert sources[1]['name'] == 'medium-priority'
assert sources[2]['name'] == 'low-priority'
source_manager.add_source(name='high-priority', git_url=git_url, priority=1, enabled=False)
enabled_sources = source_manager.list_sources(enabled_only=True)
assert len(enabled_sources) == 2
assert all((s['enabled'] for s in enabled_sources))
assert 'high-priority' not in [s['name'] for s in enabled_sources]
```

## Next Steps


---

*Source: test_git_sources_e2e.py:225 | Complexity: Advanced | Last updated: 2026-02-14*