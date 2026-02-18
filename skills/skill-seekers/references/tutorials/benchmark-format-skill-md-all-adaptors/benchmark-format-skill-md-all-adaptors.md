# How To: Benchmark Format Skill Md All Adaptors

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Benchmark format_skill_md across all adaptors

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

### Step 1: 'Benchmark format_skill_md across all adaptors'

```python
'Benchmark format_skill_md across all adaptors'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: format_skill_md() - All Adaptors')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign skill_dir = self._create_skill_with_n_references(...)

```python
skill_dir = self._create_skill_with_n_references(10)
```

### Step 6: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='benchmark', description='Benchmark test')
```

### Step 7: Assign platforms = value

```python
platforms = ['claude', 'gemini', 'openai', 'markdown', 'langchain', 'llama-index', 'haystack', 'weaviate', 'chroma', 'faiss', 'qdrant']
```

### Step 8: Assign results = value

```python
results = {}
```

### Step 9: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 10: Call adaptor.format_skill_md()

```python
adaptor.format_skill_md(skill_dir, metadata)
```

### Step 11: Assign times = value

```python
times = []
```

### Step 12: Assign avg_time = value

```python
avg_time = sum(times) / len(times)
```

### Step 13: Assign min_time = min(...)

```python
min_time = min(times)
```

### Step 14: Assign max_time = max(...)

```python
max_time = max(times)
```

### Step 15: Assign unknown = value

```python
results[platform] = {'avg': avg_time, 'min': min_time, 'max': max_time}
```

### Step 16: Call print()

```python
print(f'{platform:15} - Avg: {avg_time * 1000:6.2f}ms | Min: {min_time * 1000:6.2f}ms | Max: {max_time * 1000:6.2f}ms')
```

### Step 17: Call self.assertLess()

```python
self.assertLess(metrics['avg'], 0.5, f"{platform} format_skill_md too slow: {metrics['avg'] * 1000:.2f}ms")
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

### Step 21: Call times.append()

```python
times.append(end - start)
```

### Step 22: Call self.assertIsInstance()

```python
self.assertIsInstance(formatted, str)
```

### Step 23: Call self.assertGreater()

```python
self.assertGreater(len(formatted), 0)
```


## Complete Example

```python
# Workflow
'Benchmark format_skill_md across all adaptors'
print('\n' + '=' * 80)
print('BENCHMARK: format_skill_md() - All Adaptors')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
metadata = SkillMetadata(name='benchmark', description='Benchmark test')
platforms = ['claude', 'gemini', 'openai', 'markdown', 'langchain', 'llama-index', 'haystack', 'weaviate', 'chroma', 'faiss', 'qdrant']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    adaptor.format_skill_md(skill_dir, metadata)
    times = []
    for _ in range(5):
        start = time.perf_counter()
        formatted = adaptor.format_skill_md(skill_dir, metadata)
        end = time.perf_counter()
        times.append(end - start)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    results[platform] = {'avg': avg_time, 'min': min_time, 'max': max_time}
    print(f'{platform:15} - Avg: {avg_time * 1000:6.2f}ms | Min: {min_time * 1000:6.2f}ms | Max: {max_time * 1000:6.2f}ms')
for platform, metrics in results.items():
    self.assertLess(metrics['avg'], 0.5, f"{platform} format_skill_md too slow: {metrics['avg'] * 1000:.2f}ms")
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:76 | Complexity: Advanced | Last updated: 2026-02-14*