# How To: Add Source Full Parameters

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test adding source with all parameters.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `pytest`
- `skill_seekers.mcp.source_manager`

**Setup Required:**
```python
# Fixtures: source_manager
```

## Step-by-Step Guide

### Step 1: 'Test adding source with all parameters.'

```python
'Test adding source with all parameters.'
```

**Verification:**
```python
assert source['name'] == 'company'
```

### Step 2: Assign source = source_manager.add_source(...)

```python
source = source_manager.add_source(name='company', git_url='https://gitlab.company.com/platform/configs.git', source_type='gitlab', token_env='CUSTOM_TOKEN', branch='develop', priority=1, enabled=False)
```

**Verification:**
```python
assert source['type'] == 'gitlab'
```


## Complete Example

```python
# Setup
# Fixtures: source_manager

# Workflow
'Test adding source with all parameters.'
source = source_manager.add_source(name='company', git_url='https://gitlab.company.com/platform/configs.git', source_type='gitlab', token_env='CUSTOM_TOKEN', branch='develop', priority=1, enabled=False)
assert source['name'] == 'company'
assert source['type'] == 'gitlab'
assert source['token_env'] == 'CUSTOM_TOKEN'
assert source['branch'] == 'develop'
assert source['priority'] == 1
assert source['enabled'] is False
```

## Next Steps


---

*Source: test_source_manager.py:98 | Complexity: Beginner | Last updated: 2026-02-14*