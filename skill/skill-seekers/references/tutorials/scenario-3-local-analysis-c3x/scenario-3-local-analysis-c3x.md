# How To: Scenario 3 Local Analysis C3X

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test C3.x analysis of local codebase.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`

**Setup Required:**
```python
# Fixtures: local_codebase
```

## Step-by-Step Guide

### Step 1: 'Test C3.x analysis of local codebase.'

```python
'Test C3.x analysis of local codebase.'
```

**Verification:**
```python
assert result.source_type == 'local'
```

### Step 2: Assign analyzer = UnifiedCodebaseAnalyzer(...)

```python
analyzer = UnifiedCodebaseAnalyzer()
```

**Verification:**
```python
assert result.analysis_depth == 'c3x'
```

### Step 3: Assign mock_c3x.return_value = value

```python
mock_c3x.return_value = {'files': ['database.py', 'api.py'], 'analysis_type': 'c3x', 'c3_1_patterns': [{'name': 'Singleton', 'count': 1, 'file': 'database.py'}], 'c3_2_examples': [{'name': 'test_connection', 'file': 'test_database.py'}], 'c3_2_examples_count': 1, 'c3_3_guides': [], 'c3_4_configs': [], 'c3_7_architecture': []}
```

**Verification:**
```python
assert result.code_analysis['analysis_type'] == 'c3x'
```

### Step 4: Assign result = analyzer.analyze(...)

```python
result = analyzer.analyze(source=str(local_codebase), depth='c3x', fetch_github_metadata=False)
```

**Verification:**
```python
assert 'c3_1_patterns' in result.code_analysis
```


## Complete Example

```python
# Setup
# Fixtures: local_codebase

# Workflow
'Test C3.x analysis of local codebase.'
analyzer = UnifiedCodebaseAnalyzer()
with patch('skill_seekers.cli.unified_codebase_analyzer.UnifiedCodebaseAnalyzer.c3x_analysis') as mock_c3x:
    mock_c3x.return_value = {'files': ['database.py', 'api.py'], 'analysis_type': 'c3x', 'c3_1_patterns': [{'name': 'Singleton', 'count': 1, 'file': 'database.py'}], 'c3_2_examples': [{'name': 'test_connection', 'file': 'test_database.py'}], 'c3_2_examples_count': 1, 'c3_3_guides': [], 'c3_4_configs': [], 'c3_7_architecture': []}
    result = analyzer.analyze(source=str(local_codebase), depth='c3x', fetch_github_metadata=False)
    assert result.source_type == 'local'
    assert result.analysis_depth == 'c3x'
    assert result.code_analysis['analysis_type'] == 'c3x'
    assert 'c3_1_patterns' in result.code_analysis
    assert 'c3_2_examples' in result.code_analysis
    assert result.github_docs is None
    assert result.github_insights is None
```

## Next Steps


---

*Source: test_architecture_scenarios.py:742 | Complexity: Intermediate | Last updated: 2026-02-14*