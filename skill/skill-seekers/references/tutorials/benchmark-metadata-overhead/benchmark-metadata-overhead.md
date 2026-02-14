# How To: Benchmark Metadata Overhead

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Measure metadata processing overhead

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `tempfile`
- `time`
- `unittest`
- `pathlib`
- `pytest`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.adaptors.base`

**Setup Required:**
```python
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()
```

## Step-by-Step Guide

### Step 1: 'Measure metadata processing overhead'

```python
'Measure metadata processing overhead'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: Metadata Processing Overhead')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign skill_dir = self._create_skill_with_n_references(...)

```python
skill_dir = self._create_skill_with_n_references(10)
```

### Step 6: Assign minimal_meta = SkillMetadata(...)

```python
minimal_meta = SkillMetadata(name='test', description='Test')
```

### Step 7: Assign rich_meta = SkillMetadata(...)

```python
rich_meta = SkillMetadata(name='test', description='A comprehensive test skill for benchmarking purposes', version='2.5.0', author='Benchmark Suite', tags=['test', 'benchmark', 'performance', 'validation', 'quality'])
```

### Step 8: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('langchain')
```

### Step 9: Assign times_minimal = value

```python
times_minimal = []
```

### Step 10: Assign times_rich = value

```python
times_rich = []
```

### Step 11: Assign avg_minimal = value

```python
avg_minimal = sum(times_minimal) / len(times_minimal)
```

### Step 12: Assign avg_rich = value

```python
avg_rich = sum(times_rich) / len(times_rich)
```

### Step 13: Assign overhead = value

```python
overhead = avg_rich - avg_minimal
```

### Step 14: Assign overhead_pct = value

```python
overhead_pct = overhead / avg_minimal * 100
```

### Step 15: Call print()

```python
print(f'\nMinimal metadata: {avg_minimal * 1000:.2f}ms')
```

### Step 16: Call print()

```python
print(f'Rich metadata:    {avg_rich * 1000:.2f}ms')
```

### Step 17: Call print()

```python
print(f'Overhead:         {overhead * 1000:.2f}ms ({overhead_pct:.1f}%)')
```

### Step 18: Call self.assertLess()

```python
self.assertLess(overhead_pct, 10.0, f'Metadata overhead too high: {overhead_pct:.1f}%')
```

### Step 19: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 20: Call adaptor.format_skill_md()

```python
adaptor.format_skill_md(skill_dir, minimal_meta)
```

### Step 21: Assign end = time.perf_counter(...)

```python
end = time.perf_counter()
```

### Step 22: Call times_minimal.append()

```python
times_minimal.append(end - start)
```

### Step 23: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 24: Call adaptor.format_skill_md()

```python
adaptor.format_skill_md(skill_dir, rich_meta)
```

### Step 25: Assign end = time.perf_counter(...)

```python
end = time.perf_counter()
```

### Step 26: Call times_rich.append()

```python
times_rich.append(end - start)
```


## Complete Example

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

# Workflow
'Measure metadata processing overhead'
print('\n' + '=' * 80)
print('BENCHMARK: Metadata Processing Overhead')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
minimal_meta = SkillMetadata(name='test', description='Test')
rich_meta = SkillMetadata(name='test', description='A comprehensive test skill for benchmarking purposes', version='2.5.0', author='Benchmark Suite', tags=['test', 'benchmark', 'performance', 'validation', 'quality'])
adaptor = get_adaptor('langchain')
times_minimal = []
for _ in range(5):
    start = time.perf_counter()
    adaptor.format_skill_md(skill_dir, minimal_meta)
    end = time.perf_counter()
    times_minimal.append(end - start)
times_rich = []
for _ in range(5):
    start = time.perf_counter()
    adaptor.format_skill_md(skill_dir, rich_meta)
    end = time.perf_counter()
    times_rich.append(end - start)
avg_minimal = sum(times_minimal) / len(times_minimal)
avg_rich = sum(times_rich) / len(times_rich)
overhead = avg_rich - avg_minimal
overhead_pct = overhead / avg_minimal * 100
print(f'\nMinimal metadata: {avg_minimal * 1000:.2f}ms')
print(f'Rich metadata:    {avg_rich * 1000:.2f}ms')
print(f'Overhead:         {overhead * 1000:.2f}ms ({overhead_pct:.1f}%)')
self.assertLess(overhead_pct, 10.0, f'Metadata overhead too high: {overhead_pct:.1f}%')
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:291 | Complexity: Advanced | Last updated: 2026-02-14*