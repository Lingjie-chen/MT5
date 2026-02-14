# How To: Completeness Full

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test completeness analysis with complete skill.

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
# Fixtures: complete_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Test completeness analysis with complete skill.'

```python
'Test completeness analysis with complete skill.'
```

**Verification:**
```python
assert score >= 70
```

### Step 2: Assign analyzer = QualityAnalyzer(...)

```python
analyzer = QualityAnalyzer(complete_skill_dir)
```

### Step 3: Assign score = analyzer.analyze_completeness(...)

```python
score = analyzer.analyze_completeness()
```

**Verification:**
```python
assert score >= 70
```


## Complete Example

```python
# Setup
# Fixtures: complete_skill_dir

# Workflow
'Test completeness analysis with complete skill.'
analyzer = QualityAnalyzer(complete_skill_dir)
score = analyzer.analyze_completeness()
assert score >= 70
```

## Next Steps


---

*Source: test_quality_metrics.py:60 | Complexity: Beginner | Last updated: 2026-02-14*