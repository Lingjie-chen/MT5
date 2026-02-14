# How To: E2E Metadata Consistency

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that metadata is consistent across platforms

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

### Step 1: 'Test that metadata is consistent across platforms'

```python
'Test that metadata is consistent across platforms'
```

### Step 2: Assign platforms_with_metadata = value

```python
platforms_with_metadata = ['gemini', 'openai', 'markdown']
```

### Step 3: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(self.skill_dir, self.output_dir)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(metadata['platform'], platform)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(metadata['name'], 'test-skill')
```

### Step 7: Call self.assertIn()

```python
self.assertIn('created_with', metadata)
```

### Step 8: Assign metadata_member = tar.getmember(...)

```python
metadata_member = tar.getmember('gemini_metadata.json')
```

### Step 9: Assign metadata_file = tar.extractfile(...)

```python
metadata_file = tar.extractfile(metadata_member)
```

### Step 10: Assign metadata = json.loads(...)

```python
metadata = json.loads(metadata_file.read().decode('utf-8'))
```

### Step 11: Assign metadata_filename = value

```python
metadata_filename = f'{platform}_metadata.json' if platform == 'openai' else 'metadata.json'
```

### Step 12: Assign metadata_content = zf.read.decode(...)

```python
metadata_content = zf.read(metadata_filename).decode('utf-8')
```

### Step 13: Assign metadata = json.loads(...)

```python
metadata = json.loads(metadata_content)
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
'Test that metadata is consistent across platforms'
platforms_with_metadata = ['gemini', 'openai', 'markdown']
for platform in platforms_with_metadata:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if platform == 'gemini':
        with tarfile.open(package_path, 'r:gz') as tar:
            metadata_member = tar.getmember('gemini_metadata.json')
            metadata_file = tar.extractfile(metadata_member)
            metadata = json.loads(metadata_file.read().decode('utf-8'))
    else:
        with zipfile.ZipFile(package_path, 'r') as zf:
            metadata_filename = f'{platform}_metadata.json' if platform == 'openai' else 'metadata.json'
            metadata_content = zf.read(metadata_filename).decode('utf-8')
            metadata = json.loads(metadata_content)
    self.assertEqual(metadata['platform'], platform)
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertIn('created_with', metadata)
```

## Next Steps


---

*Source: test_adaptors_e2e.py:357 | Complexity: Advanced | Last updated: 2026-02-14*