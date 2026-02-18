# How To: Comparison Report Overall Improvement

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test ComparisonReport overall_improvement property.

## Prerequisites

**Required Modules:**
- `pytest`
- `time`
- `json`
- `datetime`
- `skill_seekers.benchmark`
- `skill_seekers.benchmark.models`
- `skill_seekers.benchmark.models`
- `os`
- `skill_seekers.benchmark.models`
- `skill_seekers.benchmark.models`


## Step-by-Step Guide

### Step 1: 'Test ComparisonReport overall_improvement property.'

```python
'Test ComparisonReport overall_improvement property.'
```

**Verification:**
```python
assert '100.0% faster' in improvement
```

### Step 2: Assign baseline = BenchmarkReport(...)

```python
baseline = BenchmarkReport(name='baseline', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=10.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
```

**Verification:**
```python
assert '✅' in improvement
```

### Step 3: Assign current = BenchmarkReport(...)

```python
current = BenchmarkReport(name='current', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=5.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
```

### Step 4: Assign comparison = ComparisonReport(...)

```python
comparison = ComparisonReport(name='test', baseline=baseline, current=current, improvements=[], regressions=[], speedup_factor=2.0, memory_change_mb=0.0)
```

### Step 5: Assign improvement = value

```python
improvement = comparison.overall_improvement
```

**Verification:**
```python
assert '100.0% faster' in improvement
```


## Complete Example

```python
# Workflow
'Test ComparisonReport overall_improvement property.'
from skill_seekers.benchmark.models import ComparisonReport
baseline = BenchmarkReport(name='baseline', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=10.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
current = BenchmarkReport(name='current', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=5.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
comparison = ComparisonReport(name='test', baseline=baseline, current=current, improvements=[], regressions=[], speedup_factor=2.0, memory_change_mb=0.0)
improvement = comparison.overall_improvement
assert '100.0% faster' in improvement
assert '✅' in improvement
```

## Next Steps


---

*Source: test_benchmark.py:586 | Complexity: Intermediate | Last updated: 2026-02-14*