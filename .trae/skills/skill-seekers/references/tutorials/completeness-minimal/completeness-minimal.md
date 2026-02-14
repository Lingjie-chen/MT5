# How To: Completeness Minimal

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test completeness analysis with minimal skill.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `skill_seekers.cli.quality_metrics`

**Setup Required:**
```python
# Fixtures: minimal_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Test completeness analysis with minimal skill.'

```python
'Test completeness analysis with minimal skill.'
```

**Verification:**
```python
assert score < 80
```

### Step 2: Assign analyzer = QualityAnalyzer(...)

```python
analyzer = QualityAnalyzer(minimal_skill_dir)
```

### Step 3: Assign score = analyzer.analyze_completeness(...)

```python
score = analyzer.analyze_completeness()
```

**Verification:**
```python
assert score < 80
```


## Complete Example

```python
# Setup
# Fixtures: minimal_skill_dir

# Workflow
'Test completeness analysis with minimal skill.'
analyzer = QualityAnalyzer(minimal_skill_dir)
score = analyzer.analyze_completeness()
assert score < 80
```

## Next Steps


---

*Source: test_quality_metrics.py:68 | Complexity: Beginner | Last updated: 2026-02-14*