# How To: Scenario 3 Local Analysis Basic

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic analysis of local codebase.

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

### Step 1: 'Test basic analysis of local codebase.'

```python
'Test basic analysis of local codebase.'
```

**Verification:**
```python
assert isinstance(result, AnalysisResult)
```

### Step 2: Assign analyzer = UnifiedCodebaseAnalyzer(...)

```python
analyzer = UnifiedCodebaseAnalyzer()
```

**Verification:**
```python
assert result.source_type == 'local'
```

### Step 3: Assign result = analyzer.analyze(...)

```python
result = analyzer.analyze(source=str(local_codebase), depth='basic', fetch_github_metadata=False)
```

**Verification:**
```python
assert result.analysis_depth == 'basic'
```


## Complete Example

```python
# Setup
# Fixtures: local_codebase

# Workflow
'Test basic analysis of local codebase.'
analyzer = UnifiedCodebaseAnalyzer()
result = analyzer.analyze(source=str(local_codebase), depth='basic', fetch_github_metadata=False)
assert isinstance(result, AnalysisResult)
assert result.source_type == 'local'
assert result.analysis_depth == 'basic'
assert result.code_analysis is not None
assert 'files' in result.code_analysis
assert len(result.code_analysis['files']) >= 2
assert result.github_docs is None
assert result.github_insights is None
```

## Next Steps


---

*Source: test_architecture_scenarios.py:720 | Complexity: Beginner | Last updated: 2026-02-14*