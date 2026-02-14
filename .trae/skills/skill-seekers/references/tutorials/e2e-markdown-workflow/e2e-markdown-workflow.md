# How To: E2E Markdown Workflow

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete Markdown workflow: package + verify structure

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

### Step 1: 'Test complete Markdown workflow: package + verify structure'

```python
'Test complete Markdown workflow: package + verify structure'
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('markdown')
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
self.assertIn('README.md', names)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('DOCUMENTATION.md', names)
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(any(('references/' in name for name in names)))
```

### Step 10: Call self.assertIn()

```python
self.assertIn('metadata.json', names)
```

### Step 11: Assign doc_content = zf.read.decode(...)

```python
doc_content = zf.read('DOCUMENTATION.md').decode('utf-8')
```

### Step 12: Call self.assertIn()

```python
self.assertIn('Getting Started', doc_content)
```

### Step 13: Call self.assertIn()

```python
self.assertIn('React Hooks', doc_content)
```

### Step 14: Call self.assertIn()

```python
self.assertIn('Components', doc_content)
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
'Test complete Markdown workflow: package + verify structure'
adaptor = get_adaptor('markdown')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('README.md', names)
    self.assertIn('DOCUMENTATION.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    self.assertIn('metadata.json', names)
    doc_content = zf.read('DOCUMENTATION.md').decode('utf-8')
    self.assertIn('Getting Started', doc_content)
    self.assertIn('React Hooks', doc_content)
    self.assertIn('Components', doc_content)
```

## Next Steps


---

*Source: test_adaptors_e2e.py:248 | Complexity: Advanced | Last updated: 2026-02-14*