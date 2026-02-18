# How To: Benchmark Json Vs Zip Size Comparison

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Compare output sizes: JSON vs ZIP/tar.gz

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

### Step 1: 'Compare output sizes: JSON vs ZIP/tar.gz'

```python
'Compare output sizes: JSON vs ZIP/tar.gz'
```

### Step 2: Call print()

```python
print('\n' + '=' * 80)
```

### Step 3: Call print()

```python
print('BENCHMARK: Output Size Comparison')
```

### Step 4: Call print()

```python
print('=' * 80)
```

### Step 5: Assign skill_dir = self._create_skill_with_n_references(...)

```python
skill_dir = self._create_skill_with_n_references(10)
```

### Step 6: Assign formats = value

```python
formats = {'claude': ('ZIP', '.zip'), 'gemini': ('tar.gz', '.tar.gz'), 'langchain': ('JSON', '.json'), 'weaviate': ('JSON', '.json')}
```

### Step 7: Assign results = value

```python
results = {}
```

### Step 8: Call print()

```python
print(f"\n{'Platform':15} | {'Format':8} | {'Size (KB)':>10}")
```

### Step 9: Call print()

```python
print('-' * 50)
```

### Step 10: Assign json_sizes = value

```python
json_sizes = [v['size_kb'] for k, v in results.items() if v['format'] == 'JSON']
```

### Step 11: Assign compressed_sizes = value

```python
compressed_sizes = [v['size_kb'] for k, v in results.items() if v['format'] in ['ZIP', 'tar.gz']]
```

### Step 12: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 13: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(skill_dir, self.output_dir)
```

### Step 14: Assign size_kb = value

```python
size_kb = package_path.stat().st_size / 1024
```

### Step 15: Assign unknown = value

```python
results[platform] = {'format': format_name, 'size_kb': size_kb}
```

### Step 16: Call print()

```python
print(f'{platform:15} | {format_name:8} | {size_kb:10.1f}')
```

### Step 17: Assign avg_json = value

```python
avg_json = sum(json_sizes) / len(json_sizes)
```

### Step 18: Assign avg_compressed = value

```python
avg_compressed = sum(compressed_sizes) / len(compressed_sizes)
```

### Step 19: Call print()

```python
print(f'\nAverage JSON size: {avg_json:.1f} KB')
```

### Step 20: Call print()

```python
print(f'Average compressed size: {avg_compressed:.1f} KB')
```

### Step 21: Call print()

```python
print(f'Compression ratio: {avg_json / avg_compressed:.2f}x')
```


## Complete Example

```python
# Workflow
'Compare output sizes: JSON vs ZIP/tar.gz'
print('\n' + '=' * 80)
print('BENCHMARK: Output Size Comparison')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
formats = {'claude': ('ZIP', '.zip'), 'gemini': ('tar.gz', '.tar.gz'), 'langchain': ('JSON', '.json'), 'weaviate': ('JSON', '.json')}
results = {}
print(f"\n{'Platform':15} | {'Format':8} | {'Size (KB)':>10}")
print('-' * 50)
for platform, (format_name, ext) in formats.items():
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(skill_dir, self.output_dir)
    size_kb = package_path.stat().st_size / 1024
    results[platform] = {'format': format_name, 'size_kb': size_kb}
    print(f'{platform:15} | {format_name:8} | {size_kb:10.1f}')
json_sizes = [v['size_kb'] for k, v in results.items() if v['format'] == 'JSON']
compressed_sizes = [v['size_kb'] for k, v in results.items() if v['format'] in ['ZIP', 'tar.gz']]
if json_sizes and compressed_sizes:
    avg_json = sum(json_sizes) / len(json_sizes)
    avg_compressed = sum(compressed_sizes) / len(compressed_sizes)
    print(f'\nAverage JSON size: {avg_json:.1f} KB')
    print(f'Average compressed size: {avg_compressed:.1f} KB')
    print(f'Compression ratio: {avg_json / avg_compressed:.2f}x')
```

## Next Steps


---

*Source: test_adaptor_benchmarks.py:245 | Complexity: Advanced | Last updated: 2026-02-14*