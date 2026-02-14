# How To: E2E Claude Workflow

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete Claude workflow: package + verify structure

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

### Step 1: 'Test complete Claude workflow: package + verify structure'

```python
'Test complete Claude workflow: package + verify structure'
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('claude')
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
self.assertIn('SKILL.md', names)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(any(('references/' in name for name in names)))
```

### Step 9: Assign skill_content = zf.read.decode(...)

```python
skill_content = zf.read('SKILL.md').decode('utf-8')
```

### Step 10: Call self.assertGreater()

```python
self.assertGreater(len(skill_content), 0)
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
'Test complete Claude workflow: package + verify structure'
adaptor = get_adaptor('claude')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('SKILL.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    skill_content = zf.read('SKILL.md').decode('utf-8')
    self.assertGreater(len(skill_content), 0)
```

## Next Steps


---

*Source: test_adaptors_e2e.py:155 | Complexity: Advanced | Last updated: 2026-02-14*