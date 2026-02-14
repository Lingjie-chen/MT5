# How To: Benchmark Scaling With Reference Count

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test how performance scales with reference count

## Prerequisites

**Required Modules:**
- `json`
- `tempfile`
- `time`
- `unittest`
- `pathlib`
- `pytest`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.adaptors.base`


## Step-by-Step Guide

### Step 1: 'Test how performance scales with reference count'

```python
'Test how performance scales with reference count'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: Scaling with Reference Count')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('langchain')
```

### Step 6: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='scaling_test', description='Scaling benchmark test')
```

### Step 7: Assign reference_counts = value

```python
reference_counts = [1, 5, 10, 25, 50]
```

### Step 8: Assign results = value

```python
results = []
```

### Step 9: Call print()

```python
print(f"\n{'Refs':>4} | {'Time (ms)':>10} | {'Time/Ref':>10} | {'Size (KB)':>10}")
```

### Step 10: Call print()

```python
print('-' * 50)
```

### Step 11: Assign first_per_ref = value

```python
first_per_ref = results[0]['time_per_ref']
```

### Step 12: Assign last_per_ref = value

```python
last_per_ref = results[-1]['time_per_ref']
```

### Step 13: Assign scaling_factor = value

```python
scaling_factor = last_per_ref / first_per_ref
```

### Step 14: Call print()

```python
print(f'\nScaling Factor: {scaling_factor:.2f}x')
```

### Step 15: Call print()

```python
print(f'(Time per ref at 50 refs / Time per ref at 1 ref)')
```

### Step 16: Call self.assertLess()

```python
self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')
```

### Step 17: Assign skill_dir = self._create_skill_with_n_references(...)

```python
skill_dir = self._create_skill_with_n_references(ref_count)
```

### Step 18: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 19: Assign formatted = adaptor.format_skill_md(...)

```python
formatted = adaptor.format_skill_md(skill_dir, metadata)
```

### Step 20: Assign end = time.perf_counter(...)

```python
end = time.perf_counter()
```

### Step 21: Assign elapsed = value

```python
elapsed = end - start
```

### Step 22: Assign time_per_ref = value

```python
time_per_ref = elapsed / ref_count
```

### Step 23: Call json.loads()

```python
json.loads(formatted)
```

### Step 24: Assign size_kb = value

```python
size_kb = len(formatted) / 1024
```

### Step 25: Call results.append()

```python
results.append({'count': ref_count, 'time': elapsed, 'time_per_ref': time_per_ref, 'size_kb': size_kb})
```

### Step 26: Call print()

```python
print(f'{ref_count:4} | {elapsed * 1000:10.2f} | {time_per_ref * 1000:10.3f} | {size_kb:10.1f}')
```


## Complete Example

```python
# Workflow
'Test how performance scales with reference count'
print('\n' + '=' * 80)
print('BENCHMARK: Scaling with Reference Count')
print('=' * 80)
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='scaling_test', description='Scaling benchmark test')
reference_counts = [1, 5, 10, 25, 50]
results = []
print(f"\n{'Refs':>4} | {'Time (ms)':>10} | {'Time/Ref':>10} | {'Size (KB)':>10}")
print('-' * 50)
for ref_count in reference_counts:
    skill_dir = self._create_skill_with_n_references(ref_count)
    start = time.perf_counter()
    formatted = adaptor.format_skill_md(skill_dir, metadata)
    end = time.perf_counter()
    elapsed = end - start
    time_per_ref = elapsed / ref_count
    json.loads(formatted)
    size_kb = len(formatted) / 1024
    results.append({'count': ref_count, 'time': elapsed, 'time_per_ref': time_per_ref, 'size_kb': size_kb})
    print(f'{ref_count:4} | {elapsed * 1000:10.2f} | {time_per_ref * 1000:10.3f} | {size_kb:10.1f}')
first_per_ref = results[0]['time_per_ref']
last_per_ref = results[-1]['time_per_ref']
scaling_factor = last_per_ref / first_per_ref
print(f'\nScaling Factor: {scaling_factor:.2f}x')
print(f'(Time per ref at 50 refs / Time per ref at 1 ref)')
self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:188 | Complexity: Advanced | Last updated: 2026-02-14*