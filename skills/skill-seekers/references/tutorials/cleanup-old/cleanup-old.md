# How To: Cleanup Old

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test cleaning up old benchmarks.

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

### Step 1: 'Test cleaning up old benchmarks.'

```python
'Test cleaning up old benchmarks.'
```

**Verification:**
```python
assert len(list(tmp_path.glob('test_*.json'))) == 10
```

### Step 2: Assign runner = BenchmarkRunner(...)

```python
runner = BenchmarkRunner(output_dir=tmp_path)
```

**Verification:**
```python
assert len(remaining) == 3
```

### Step 3: Assign base_time = time.time(...)

```python
base_time = time.time()
```

**Verification:**
```python
assert 'test_00000007' in remaining_names or 'test_00000008' in remaining_names
```

### Step 4: Call runner.cleanup_old()

```python
runner.cleanup_old(keep_latest=3)
```

### Step 5: Assign remaining = list(...)

```python
remaining = list(tmp_path.glob('test_*.json'))
```

**Verification:**
```python
assert len(remaining) == 3
```

### Step 6: Assign remaining_names = value

```python
remaining_names = {f.stem for f in remaining}
```

**Verification:**
```python
assert 'test_00000007' in remaining_names or 'test_00000008' in remaining_names
```

### Step 7: Assign filename = value

```python
filename = f'test_{i:08d}.json'
```

### Step 8: Assign file_path = value

```python
file_path = tmp_path / filename
```

### Step 9: Assign report_data = value

```python
report_data = {'name': 'test', 'started_at': datetime.utcnow().isoformat(), 'finished_at': datetime.utcnow().isoformat(), 'total_duration': 1.0, 'timings': [], 'memory': [], 'metrics': [], 'system_info': {}, 'recommendations': []}
```

### Step 10: Assign mtime = value

```python
mtime = base_time - (10 - i) * 60
```

### Step 11: Call os.utime()

```python
os.utime(file_path, (mtime, mtime))
```

### Step 12: Call json.dump()

```python
json.dump(report_data, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test cleaning up old benchmarks.'
import os
runner = BenchmarkRunner(output_dir=tmp_path)
base_time = time.time()
for i in range(10):
    filename = f'test_{i:08d}.json'
    file_path = tmp_path / filename
    report_data = {'name': 'test', 'started_at': datetime.utcnow().isoformat(), 'finished_at': datetime.utcnow().isoformat(), 'total_duration': 1.0, 'timings': [], 'memory': [], 'metrics': [], 'system_info': {}, 'recommendations': []}
    with open(file_path, 'w') as f:
        json.dump(report_data, f)
    mtime = base_time - (10 - i) * 60
    os.utime(file_path, (mtime, mtime))
assert len(list(tmp_path.glob('test_*.json'))) == 10
runner.cleanup_old(keep_latest=3)
remaining = list(tmp_path.glob('test_*.json'))
assert len(remaining) == 3
remaining_names = {f.stem for f in remaining}
assert 'test_00000007' in remaining_names or 'test_00000008' in remaining_names
```

## Next Steps


---

*Source: test_benchmark.py:441 | Complexity: Advanced | Last updated: 2026-02-14*