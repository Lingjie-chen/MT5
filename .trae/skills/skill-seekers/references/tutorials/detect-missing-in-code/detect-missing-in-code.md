# How To: Detect Missing In Code

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of APIs missing in code

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


## Step-by-Step Guide

### Step 1: 'Test detection of APIs missing in code'

```python
'Test detection of APIs missing in code'
```

**Verification:**
```python
assert len(conflicts) > 0
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'obsolete_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
```

**Verification:**
```python
assert any((c.type == 'missing_in_code' for c in conflicts))
```

### Step 3: Assign github_data = value

```python
github_data = {'code_analysis': {'analyzed_files': []}}
```

**Verification:**
```python
assert any((c.api_name == 'obsolete_func' for c in conflicts))
```

### Step 4: Assign detector = ConflictDetector(...)

```python
detector = ConflictDetector(docs_data, github_data)
```

### Step 5: Assign conflicts = detector._find_missing_in_code(...)

```python
conflicts = detector._find_missing_in_code()
```

**Verification:**
```python
assert len(conflicts) > 0
```


## Complete Example

```python
# Workflow
'Test detection of APIs missing in code'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'obsolete_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': []}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_missing_in_code()
assert len(conflicts) > 0
assert any((c.type == 'missing_in_code' for c in conflicts))
assert any((c.api_name == 'obsolete_func' for c in conflicts))
```

## Next Steps


---

*Source: test_unified.py:193 | Complexity: Intermediate | Last updated: 2026-02-14*