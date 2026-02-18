# How To: Merge Summary

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test merge summary statistics

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

### Step 1: 'Test merge summary statistics'

```python
'Test merge summary statistics'
```

**Verification:**
```python
assert 'summary' in merged
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'api1', 'parameters': [], 'return_type': 'str'}, {'name': 'api2', 'parameters': [], 'return_type': 'int'}]}]}
```

**Verification:**
```python
assert merged['summary']['total_apis'] == 3
```

### Step 3: Assign github_data = value

```python
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'api3', 'parameters': [], 'return_type': 'bool'}]}]}}
```

**Verification:**
```python
assert merged['summary']['docs_only'] == 2
```

### Step 4: Assign detector = ConflictDetector(...)

```python
detector = ConflictDetector(docs_data, github_data)
```

**Verification:**
```python
assert merged['summary']['code_only'] == 1
```

### Step 5: Assign conflicts = detector.detect_all_conflicts(...)

```python
conflicts = detector.detect_all_conflicts()
```

### Step 6: Assign merger = RuleBasedMerger(...)

```python
merger = RuleBasedMerger(docs_data, github_data, conflicts)
```

### Step 7: Assign merged = merger.merge_all(...)

```python
merged = merger.merge_all()
```

**Verification:**
```python
assert 'summary' in merged
```


## Complete Example

```python
# Workflow
'Test merge summary statistics'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'api1', 'parameters': [], 'return_type': 'str'}, {'name': 'api2', 'parameters': [], 'return_type': 'int'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'api3', 'parameters': [], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'summary' in merged
assert merged['summary']['total_apis'] == 3
assert merged['summary']['docs_only'] == 2
assert merged['summary']['code_only'] == 1
```

## Next Steps


---

*Source: test_unified.py:399 | Complexity: Intermediate | Last updated: 2026-02-14*