# How To: E2E All Platforms Preserve References

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that all platforms preserve reference files

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `tarfile`
- `tempfile`
- `unittest`
- `zipfile`
- `pathlib`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.adaptors.base`
- `chromadb`

**Setup Required:**
```python
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()
```

## Step-by-Step Guide

### Step 1: 'Test that all platforms preserve reference files'

```python
'Test that all platforms preserve reference files'
```

### Step 2: Assign ref_files = value

```python
ref_files = ['getting_started.md', 'hooks.md', 'components.md']
```

### Step 3: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(self.skill_dir, self.output_dir)
```

### Step 5: Assign names = tar.getnames(...)

```python
names = tar.getnames()
```

### Step 6: Assign names = zf.namelist(...)

```python
names = zf.namelist()
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(any((f'vector_store_files/{ref_file}' in name for name in names)), f'{platform}: {ref_file} not found in vector_store_files/')
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
```


## Complete Example

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

# Workflow
'Test that all platforms preserve reference files'
ref_files = ['getting_started.md', 'hooks.md', 'components.md']
for platform in ['claude', 'gemini', 'openai', 'markdown']:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if platform == 'gemini':
        with tarfile.open(package_path, 'r:gz') as tar:
            names = tar.getnames()
            for ref_file in ref_files:
                self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
    else:
        with zipfile.ZipFile(package_path, 'r') as zf:
            names = zf.namelist()
            for ref_file in ref_files:
                if platform == 'openai':
                    self.assertTrue(any((f'vector_store_files/{ref_file}' in name for name in names)), f'{platform}: {ref_file} not found in vector_store_files/')
                else:
                    self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
```

## Next Steps


---

*Source: test_adaptors_e2e.py:324 | Complexity: Advanced | Last updated: 2026-02-14*