# How To: Detect Missing In Docs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of APIs missing in documentation

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

### Step 1: 'Test detection of APIs missing in documentation'

```python
'Test detection of APIs missing in documentation'
```

**Verification:**
```python
assert len(conflicts) > 0
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'documented_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
```

**Verification:**
```python
assert any((c.type == 'missing_in_docs' for c in conflicts))
```

### Step 3: Assign github_data = value

```python
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'undocumented_func', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
```

**Verification:**
```python
assert any((c.api_name == 'undocumented_func' for c in conflicts))
```

### Step 4: Assign detector = ConflictDetector(...)

```python
detector = ConflictDetector(docs_data, github_data)
```

### Step 5: Assign conflicts = detector._find_missing_in_docs(...)

```python
conflicts = detector._find_missing_in_docs()
```

**Verification:**
```python
assert len(conflicts) > 0
```


## Complete Example

```python
# Workflow
'Test detection of APIs missing in documentation'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'documented_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'undocumented_func', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_missing_in_docs()
assert len(conflicts) > 0
assert any((c.type == 'missing_in_docs' for c in conflicts))
assert any((c.api_name == 'undocumented_func' for c in conflicts))
```

## Next Steps


---

*Source: test_unified.py:152 | Complexity: Intermediate | Last updated: 2026-02-14*