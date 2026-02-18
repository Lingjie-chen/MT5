# How To: Compare Benchmarks

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test comparing benchmarks.

## Prerequisites

- [ ] Setup code must be executed first

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

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test comparing benchmarks.'

```python
'Test comparing benchmarks.'
```

**Verification:**
```python
assert isinstance(comparison, ComparisonReport)
```

### Step 2: Assign runner = BenchmarkRunner(...)

```python
runner = BenchmarkRunner(output_dir=tmp_path)
```

**Verification:**
```python
assert comparison.speedup_factor > 1.0
```

### Step 3: Call runner.run()

```python
runner.run('baseline', baseline_bench, save=True)
```

**Verification:**
```python
assert len(comparison.improvements) > 0
```

### Step 4: Assign baseline_path = value

```python
baseline_path = list(tmp_path.glob('baseline_*.json'))[0]
```

### Step 5: Call runner.run()

```python
runner.run('improved', improved_bench, save=True)
```

### Step 6: Assign improved_path = value

```python
improved_path = list(tmp_path.glob('improved_*.json'))[0]
```

### Step 7: Assign comparison = runner.compare(...)

```python
comparison = runner.compare(baseline_path, improved_path)
```

**Verification:**
```python
assert isinstance(comparison, ComparisonReport)
```

### Step 8: Call time.sleep()

```python
time.sleep(0.1)
```

### Step 9: Call time.sleep()

```python
time.sleep(0.05)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test comparing benchmarks.'
runner = BenchmarkRunner(output_dir=tmp_path)

def baseline_bench(bench):
    with bench.timer('operation'):
        time.sleep(0.1)
runner.run('baseline', baseline_bench, save=True)
baseline_path = list(tmp_path.glob('baseline_*.json'))[0]

def improved_bench(bench):
    with bench.timer('operation'):
        time.sleep(0.05)
runner.run('improved', improved_bench, save=True)
improved_path = list(tmp_path.glob('improved_*.json'))[0]
from skill_seekers.benchmark.models import ComparisonReport
comparison = runner.compare(baseline_path, improved_path)
assert isinstance(comparison, ComparisonReport)
assert comparison.speedup_factor > 1.0
assert len(comparison.improvements) > 0
```

## Next Steps


---

*Source: test_benchmark.py:368 | Complexity: Advanced | Last updated: 2026-02-14*