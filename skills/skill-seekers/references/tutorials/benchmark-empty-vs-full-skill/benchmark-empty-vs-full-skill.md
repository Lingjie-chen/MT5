# How To: Benchmark Empty Vs Full Skill

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Compare performance: empty skill vs full skill

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

### Step 1: 'Compare performance: empty skill vs full skill'

```python
'Compare performance: empty skill vs full skill'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: Empty vs Full Skill')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('chroma')
```

### Step 6: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='test', description='Test benchmark')
```

### Step 7: Assign empty_dir = value

```python
empty_dir = Path(self.temp_dir.name) / 'empty'
```

### Step 8: Call empty_dir.mkdir()

```python
empty_dir.mkdir()
```

### Step 9: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 10: Call adaptor.format_skill_md()

```python
adaptor.format_skill_md(empty_dir, metadata)
```

### Step 11: Assign empty_time = value

```python
empty_time = time.perf_counter() - start
```

### Step 12: Assign full_dir = self._create_skill_with_n_references(...)

```python
full_dir = self._create_skill_with_n_references(50)
```

### Step 13: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 14: Call adaptor.format_skill_md()

```python
adaptor.format_skill_md(full_dir, metadata)
```

### Step 15: Assign full_time = value

```python
full_time = time.perf_counter() - start
```

### Step 16: Call print()

```python
print(f'\nEmpty skill: {empty_time * 1000:.2f}ms')
```

### Step 17: Call print()

```python
print(f'Full skill (50 refs): {full_time * 1000:.2f}ms')
```

### Step 18: Call print()

```python
print(f'Ratio: {full_time / empty_time:.1f}x')
```

### Step 19: Call self.assertLess()

```python
self.assertLess(empty_time, 0.01, 'Empty skill processing too slow')
```

### Step 20: Call self.assertLess()

```python
self.assertLess(full_time, 0.5, 'Full skill processing too slow')
```


## Complete Example

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

# Workflow
'Compare performance: empty skill vs full skill'
print('\n' + '=' * 80)
print('BENCHMARK: Empty vs Full Skill')
print('=' * 80)
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='test', description='Test benchmark')
empty_dir = Path(self.temp_dir.name) / 'empty'
empty_dir.mkdir()
start = time.perf_counter()
adaptor.format_skill_md(empty_dir, metadata)
empty_time = time.perf_counter() - start
full_dir = self._create_skill_with_n_references(50)
start = time.perf_counter()
adaptor.format_skill_md(full_dir, metadata)
full_time = time.perf_counter() - start
print(f'\nEmpty skill: {empty_time * 1000:.2f}ms')
print(f'Full skill (50 refs): {full_time * 1000:.2f}ms')
print(f'Ratio: {full_time / empty_time:.1f}x')
self.assertLess(empty_time, 0.01, 'Empty skill processing too slow')
self.assertLess(full_time, 0.5, 'Full skill processing too slow')
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:342 | Complexity: Advanced | Last updated: 2026-02-14*