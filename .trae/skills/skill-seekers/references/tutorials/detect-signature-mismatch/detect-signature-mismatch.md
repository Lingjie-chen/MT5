# How To: Detect Signature Mismatch

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of signature mismatches

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

### Step 1: 'Test detection of signature mismatches'

```python
'Test detection of signature mismatches'
```

**Verification:**
```python
assert len(conflicts) > 0
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
```

**Verification:**
```python
assert any((c.type == 'signature_mismatch' for c in conflicts))
```

### Step 3: Assign github_data = value

```python
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'func', 'parameters': [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'bool', 'default': 'False'}], 'return_type': 'str'}]}]}}
```

**Verification:**
```python
assert any((c.api_name == 'func' for c in conflicts))
```

### Step 4: Assign detector = ConflictDetector(...)

```python
detector = ConflictDetector(docs_data, github_data)
```

### Step 5: Assign conflicts = detector._find_signature_mismatches(...)

```python
conflicts = detector._find_signature_mismatches()
```

**Verification:**
```python
assert len(conflicts) > 0
```


## Complete Example

```python
# Workflow
'Test detection of signature mismatches'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'func', 'parameters': [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'bool', 'default': 'False'}], 'return_type': 'str'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_signature_mismatches()
assert len(conflicts) > 0
assert any((c.type == 'signature_mismatch' for c in conflicts))
assert any((c.api_name == 'func' for c in conflicts))
```

## Next Steps


---

*Source: test_unified.py:220 | Complexity: Intermediate | Last updated: 2026-02-14*