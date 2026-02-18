# How To: Generate Hybrid Content With Conflicts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test hybrid content with conflicts.

## Prerequisites

**Required Modules:**
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`


## Step-by-Step Guide

### Step 1: 'Test hybrid content with conflicts.'

```python
'Test hybrid content with conflicts.'
```

**Verification:**
```python
assert hybrid['conflict_summary']['total_conflicts'] == 2
```

### Step 2: Assign api_data = value

```python
api_data = {'apis': {}, 'summary': {}}
```

**Verification:**
```python
assert hybrid['conflict_summary']['by_type']['signature_mismatch'] == 1
```

### Step 3: Assign github_docs = None

```python
github_docs = None
```

**Verification:**
```python
assert hybrid['conflict_summary']['by_type']['missing_in_docs'] == 1
```

### Step 4: Assign github_insights = None

```python
github_insights = None
```

**Verification:**
```python
assert hybrid['conflict_summary']['by_severity']['medium'] == 1
```

### Step 5: Assign conflicts = value

```python
conflicts = [Conflict(api_name='test_api', type='signature_mismatch', severity='medium', difference='Parameter count differs', docs_info={'parameters': ['a', 'b']}, code_info={'parameters': ['a', 'b', 'c']}), Conflict(api_name='test_api_2', type='missing_in_docs', severity='low', difference='API not documented', docs_info=None, code_info={'name': 'test_api_2'})]
```

**Verification:**
```python
assert hybrid['conflict_summary']['by_severity']['low'] == 1
```

### Step 6: Assign hybrid = generate_hybrid_content(...)

```python
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
```

**Verification:**
```python
assert hybrid['conflict_summary']['total_conflicts'] == 2
```


## Complete Example

```python
# Workflow
'Test hybrid content with conflicts.'
api_data = {'apis': {}, 'summary': {}}
github_docs = None
github_insights = None
conflicts = [Conflict(api_name='test_api', type='signature_mismatch', severity='medium', difference='Parameter count differs', docs_info={'parameters': ['a', 'b']}, code_info={'parameters': ['a', 'b', 'c']}), Conflict(api_name='test_api_2', type='missing_in_docs', severity='low', difference='API not documented', docs_info=None, code_info={'name': 'test_api_2'})]
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
assert hybrid['conflict_summary']['total_conflicts'] == 2
assert hybrid['conflict_summary']['by_type']['signature_mismatch'] == 1
assert hybrid['conflict_summary']['by_type']['missing_in_docs'] == 1
assert hybrid['conflict_summary']['by_severity']['medium'] == 1
assert hybrid['conflict_summary']['by_severity']['low'] == 1
```

## Next Steps


---

*Source: test_merge_sources_github.py:196 | Complexity: Intermediate | Last updated: 2026-02-14*