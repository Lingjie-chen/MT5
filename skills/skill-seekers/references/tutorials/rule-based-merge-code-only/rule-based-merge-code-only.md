# How To: Rule Based Merge Code Only

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test rule-based merge for code-only APIs

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

### Step 1: 'Test rule-based merge for code-only APIs'

```python
'Test rule-based merge for code-only APIs'
```

**Verification:**
```python
assert 'apis' in merged
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': []}
```

**Verification:**
```python
assert 'code_only_api' in merged['apis']
```

### Step 3: Assign github_data = value

```python
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'code_only_api', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
```

**Verification:**
```python
assert merged['apis']['code_only_api']['status'] == 'code_only'
```

### Step 4: Assign detector = ConflictDetector(...)

```python
detector = ConflictDetector(docs_data, github_data)
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
assert 'apis' in merged
```


## Complete Example

```python
# Workflow
'Test rule-based merge for code-only APIs'
docs_data = {'pages': []}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'code_only_api', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'apis' in merged
assert 'code_only_api' in merged['apis']
assert merged['apis']['code_only_api']['status'] == 'code_only'
```

## Next Steps


---

*Source: test_unified.py:324 | Complexity: Intermediate | Last updated: 2026-02-14*