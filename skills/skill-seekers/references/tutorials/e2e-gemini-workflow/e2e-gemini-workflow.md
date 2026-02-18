# How To: E2E Gemini Workflow

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete Gemini workflow: package + verify structure

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

### Step 1: 'Test complete Gemini workflow: package + verify structure'

```python
'Test complete Gemini workflow: package + verify structure'
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('gemini')
```

### Step 3: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(self.skill_dir, self.output_dir)
```

### Step 4: Call self.assertTrue()

```python
self.assertTrue(package_path.exists())
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(str(package_path).endswith('.tar.gz'))
```

### Step 6: Assign names = tar.getnames(...)

```python
names = tar.getnames()
```

### Step 7: Call self.assertIn()

```python
self.assertIn('system_instructions.md', names)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(any(('references/' in name for name in names)))
```

### Step 9: Call self.assertIn()

```python
self.assertIn('gemini_metadata.json', names)
```

### Step 10: Assign metadata_member = tar.getmember(...)

```python
metadata_member = tar.getmember('gemini_metadata.json')
```

### Step 11: Assign metadata_file = tar.extractfile(...)

```python
metadata_file = tar.extractfile(metadata_member)
```

### Step 12: Assign metadata = json.loads(...)

```python
metadata = json.loads(metadata_file.read().decode('utf-8'))
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(metadata['platform'], 'gemini')
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(metadata['name'], 'test-skill')
```

### Step 15: Call self.assertIn()

```python
self.assertIn('created_with', metadata)
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
'Test complete Gemini workflow: package + verify structure'
adaptor = get_adaptor('gemini')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.tar.gz'))
with tarfile.open(package_path, 'r:gz') as tar:
    names = tar.getnames()
    self.assertIn('system_instructions.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    self.assertIn('gemini_metadata.json', names)
    metadata_member = tar.getmember('gemini_metadata.json')
    metadata_file = tar.extractfile(metadata_member)
    metadata = json.loads(metadata_file.read().decode('utf-8'))
    self.assertEqual(metadata['platform'], 'gemini')
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertIn('created_with', metadata)
```

## Next Steps


---

*Source: test_adaptors_e2e.py:182 | Complexity: Advanced | Last updated: 2026-02-14*