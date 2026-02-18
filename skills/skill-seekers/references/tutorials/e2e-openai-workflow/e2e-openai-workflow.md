# How To: E2E Openai Workflow

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete OpenAI workflow: package + verify structure

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

### Step 1: 'Test complete OpenAI workflow: package + verify structure'

```python
'Test complete OpenAI workflow: package + verify structure'
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('openai')
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
self.assertTrue(str(package_path).endswith('.zip'))
```

### Step 6: Assign names = zf.namelist(...)

```python
names = zf.namelist()
```

### Step 7: Call self.assertIn()

```python
self.assertIn('assistant_instructions.txt', names)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(any(('vector_store_files/' in name for name in names)))
```

### Step 9: Call self.assertIn()

```python
self.assertIn('openai_metadata.json', names)
```

### Step 10: Assign metadata_content = zf.read.decode(...)

```python
metadata_content = zf.read('openai_metadata.json').decode('utf-8')
```

### Step 11: Assign metadata = json.loads(...)

```python
metadata = json.loads(metadata_content)
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(metadata['platform'], 'openai')
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(metadata['name'], 'test-skill')
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(metadata['model'], 'gpt-4o')
```

### Step 15: Call self.assertIn()

```python
self.assertIn('file_search', metadata['tools'])
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
'Test complete OpenAI workflow: package + verify structure'
adaptor = get_adaptor('openai')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('assistant_instructions.txt', names)
    self.assertTrue(any(('vector_store_files/' in name for name in names)))
    self.assertIn('openai_metadata.json', names)
    metadata_content = zf.read('openai_metadata.json').decode('utf-8')
    metadata = json.loads(metadata_content)
    self.assertEqual(metadata['platform'], 'openai')
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertEqual(metadata['model'], 'gpt-4o')
    self.assertIn('file_search', metadata['tools'])
```

## Next Steps


---

*Source: test_adaptors_e2e.py:215 | Complexity: Advanced | Last updated: 2026-02-14*