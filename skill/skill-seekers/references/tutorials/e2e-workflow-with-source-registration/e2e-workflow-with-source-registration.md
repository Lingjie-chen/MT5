# How To: E2E Workflow With Source Registration

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2E Test 2: Complete workflow with source registration

Steps:
1. Add source to registry
2. List sources
3. Get source details
4. Clone via source name
5. Fetch config
6. Update source (re-add with different priority)
7. Remove source
8. Verify removal

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

### Step 1: '\n        E2E Test 2: Complete workflow with source registration\n\n        Steps:\n        1. Add source to registry\n        2. List sources\n        3. Get source details\n        4. Clone via source name\n        5. Fetch config\n        6. Update source (re-add with different priority)\n        7. Remove source\n        8. Verify removal\n        '

```python
'\n        E2E Test 2: Complete workflow with source registration\n\n        Steps:\n        1. Add source to registry\n        2. List sources\n        3. Get source details\n        4. Clone via source name\n        5. Fetch config\n        6. Update source (re-add with different priority)\n        7. Remove source\n        8. Verify removal\n        '
```

**Verification:**
```python
assert source['name'] == 'team-configs'
```

### Step 2: Assign unknown = temp_dirs

```python
cache_dir, config_dir = temp_dirs
```

**Verification:**
```python
assert source['git_url'] == git_url
```

### Step 3: Assign unknown = temp_git_repo

```python
repo_dir, repo = temp_git_repo
```

**Verification:**
```python
assert source['type'] == 'custom'
```

### Step 4: Assign git_url = value

```python
git_url = f'file://{repo_dir}'
```

**Verification:**
```python
assert source['branch'] == 'master'
```

### Step 5: Assign source_manager = SourceManager(...)

```python
source_manager = SourceManager(config_dir=config_dir)
```

**Verification:**
```python
assert source['priority'] == 10
```

### Step 6: Assign source = source_manager.add_source(...)

```python
source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=10)
```

**Verification:**
```python
assert source['enabled'] is True
```

### Step 7: Assign sources = source_manager.list_sources(...)

```python
sources = source_manager.list_sources()
```

**Verification:**
```python
assert len(sources) == 1
```

### Step 8: Assign retrieved_source = source_manager.get_source(...)

```python
retrieved_source = source_manager.get_source('team-configs')
```

**Verification:**
```python
assert sources[0]['name'] == 'team-configs'
```

### Step 9: Assign git_repo = GitConfigRepo(...)

```python
git_repo = GitConfigRepo(cache_dir=cache_dir)
```

**Verification:**
```python
assert retrieved_source['git_url'] == git_url
```

### Step 10: Assign repo_path = git_repo.clone_or_pull(...)

```python
repo_path = git_repo.clone_or_pull(source_name=source['name'], git_url=source['git_url'], branch=source['branch'])
```

**Verification:**
```python
assert repo_path.exists()
```

### Step 11: Assign config = git_repo.get_config(...)

```python
config = git_repo.get_config(repo_path, 'vue')
```

**Verification:**
```python
assert config['name'] == 'vue'
```

### Step 12: Assign updated_source = source_manager.add_source(...)

```python
updated_source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=5)
```

**Verification:**
```python
assert config['base_url'] == 'https://vuejs.org/'
```

### Step 13: Assign removed = source_manager.remove_source(...)

```python
removed = source_manager.remove_source('team-configs')
```

**Verification:**
```python
assert updated_source['priority'] == 5
```

### Step 14: Assign sources = source_manager.list_sources(...)

```python
sources = source_manager.list_sources()
```

**Verification:**
```python
assert removed is True
```

### Step 15: Call source_manager.get_source()

```python
source_manager.get_source('team-configs')
```

**Verification:**
```python
assert len(sources) == 0
```


## Complete Example

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

# Workflow
'\n        E2E Test 2: Complete workflow with source registration\n\n        Steps:\n        1. Add source to registry\n        2. List sources\n        3. Get source details\n        4. Clone via source name\n        5. Fetch config\n        6. Update source (re-add with different priority)\n        7. Remove source\n        8. Verify removal\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
source_manager = SourceManager(config_dir=config_dir)
source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=10)
assert source['name'] == 'team-configs'
assert source['git_url'] == git_url
assert source['type'] == 'custom'
assert source['branch'] == 'master'
assert source['priority'] == 10
assert source['enabled'] is True
sources = source_manager.list_sources()
assert len(sources) == 1
assert sources[0]['name'] == 'team-configs'
retrieved_source = source_manager.get_source('team-configs')
assert retrieved_source['git_url'] == git_url
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name=source['name'], git_url=source['git_url'], branch=source['branch'])
assert repo_path.exists()
config = git_repo.get_config(repo_path, 'vue')
assert config['name'] == 'vue'
assert config['base_url'] == 'https://vuejs.org/'
updated_source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=5)
assert updated_source['priority'] == 5
removed = source_manager.remove_source('team-configs')
assert removed is True
sources = source_manager.list_sources()
assert len(sources) == 0
with pytest.raises(KeyError, match="Source 'team-configs' not found"):
    source_manager.get_source('team-configs')
```

## Next Steps


---

*Source: test_git_sources_e2e.py:150 | Complexity: Advanced | Last updated: 2026-02-14*