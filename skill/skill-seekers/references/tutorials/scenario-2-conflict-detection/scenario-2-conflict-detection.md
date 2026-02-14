# How To: Scenario 2 Conflict Detection

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test conflict detection between docs and code.

## Prerequisites

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`


## Step-by-Step Guide

### Step 1: 'Test conflict detection between docs and code.'

```python
'Test conflict detection between docs and code.'
```

**Verification:**
```python
assert 'GoogleProvider' in api_data
```

### Step 2: Assign api_data = value

```python
api_data = {'GoogleProvider': {'params': ['app_id', 'app_secret'], 'source': 'html_docs'}}
```

**Verification:**
```python
assert 'params' in api_data['GoogleProvider']
```

### Step 3: Assign github_docs = value

```python
github_docs = {'readme': 'Use client_id and client_secret for Google OAuth'}
```

**Verification:**
```python
assert github_docs is not None
```


## Complete Example

```python
# Workflow
'Test conflict detection between docs and code.'
api_data = {'GoogleProvider': {'params': ['app_id', 'app_secret'], 'source': 'html_docs'}}
github_docs = {'readme': 'Use client_id and client_secret for Google OAuth'}
assert 'GoogleProvider' in api_data
assert 'params' in api_data['GoogleProvider']
assert github_docs is not None
```

## Next Steps


---

*Source: test_architecture_scenarios.py:574 | Complexity: Beginner | Last updated: 2026-02-14*