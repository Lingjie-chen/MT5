# How To: Needs Api Merge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test API merge detection

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `tempfile`
- `pathlib`
- `pytest`
- `skill_seekers.cli.config_validator`
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_skill_builder`
- `json`
- `tempfile`

**Required Fixtures:**
- `api_client` fixture


## Step-by-Step Guide

### Step 1: 'Test API merge detection'

```python
'Test API merge detection'
```

**Verification:**
```python
assert validator.needs_api_merge()
```

### Step 2: Assign config_needs_merge = value

```python
config_needs_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com', 'extract_api': True}, {'type': 'github', 'repo': 'user/repo', 'include_code': True}]}
```

**Verification:**
```python
assert not validator.needs_api_merge()
```

### Step 3: Assign validator = ConfigValidator(...)

```python
validator = ConfigValidator(config_needs_merge)
```

**Verification:**
```python
assert validator.needs_api_merge()
```

### Step 4: Assign config_no_merge = value

```python
config_no_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
```

### Step 5: Assign validator = ConfigValidator(...)

```python
validator = ConfigValidator(config_no_merge)
```

**Verification:**
```python
assert not validator.needs_api_merge()
```


## Complete Example

```python
# Workflow
'Test API merge detection'
config_needs_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com', 'extract_api': True}, {'type': 'github', 'repo': 'user/repo', 'include_code': True}]}
validator = ConfigValidator(config_needs_merge)
assert validator.needs_api_merge()
config_no_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
validator = ConfigValidator(config_no_merge)
assert not validator.needs_api_merge()
```

## Next Steps


---

*Source: test_unified.py:99 | Complexity: Intermediate | Last updated: 2026-02-14*