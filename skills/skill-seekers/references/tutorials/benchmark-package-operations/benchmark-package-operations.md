# How To: Benchmark Package Operations

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Benchmark complete package operation

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

### Step 1: 'Benchmark complete package operation'

```python
'Benchmark complete package operation'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: package() - Complete Operation')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign skill_dir = self._create_skill_with_n_references(...)

```python
skill_dir = self._create_skill_with_n_references(10)
```

### Step 6: Assign platforms = value

```python
platforms = ['claude', 'langchain', 'chroma', 'weaviate', 'faiss']
```

### Step 7: Assign results = value

```python
results = {}
```

### Step 8: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 9: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

### Step 10: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(skill_dir, self.output_dir)
```

### Step 11: Assign end = time.perf_counter(...)

```python
end = time.perf_counter()
```

### Step 12: Assign elapsed = value

```python
elapsed = end - start
```

### Step 13: Assign file_size_kb = value

```python
file_size_kb = package_path.stat().st_size / 1024
```

### Step 14: Assign unknown = value

```python
results[platform] = {'time': elapsed, 'size_kb': file_size_kb}
```

### Step 15: Call print()

```python
print(f'{platform:15} - Time: {elapsed * 1000:7.2f}ms | Size: {file_size_kb:7.1f} KB')
```

### Step 16: Call self.assertTrue()

```python
self.assertTrue(package_path.exists())
```

### Step 17: Call self.assertLess()

```python
self.assertLess(metrics['time'], 1.0, f"{platform} packaging too slow: {metrics['time'] * 1000:.2f}ms")
```

### Step 18: Call self.assertLess()

```python
self.assertLess(metrics['size_kb'], 1000, f"{platform} package too large: {metrics['size_kb']:.1f}KB")
```


## Complete Example

```python
# Workflow
'Benchmark complete package operation'
print('\n' + '=' * 80)
print('BENCHMARK: package() - Complete Operation')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
platforms = ['claude', 'langchain', 'chroma', 'weaviate', 'faiss']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    start = time.perf_counter()
    package_path = adaptor.package(skill_dir, self.output_dir)
    end = time.perf_counter()
    elapsed = end - start
    file_size_kb = package_path.stat().st_size / 1024
    results[platform] = {'time': elapsed, 'size_kb': file_size_kb}
    print(f'{platform:15} - Time: {elapsed * 1000:7.2f}ms | Size: {file_size_kb:7.1f} KB')
    self.assertTrue(package_path.exists())
for platform, metrics in results.items():
    self.assertLess(metrics['time'], 1.0, f"{platform} packaging too slow: {metrics['time'] * 1000:.2f}ms")
    self.assertLess(metrics['size_kb'], 1000, f"{platform} package too large: {metrics['size_kb']:.1f}KB")
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:141 | Complexity: Advanced | Last updated: 2026-02-14*