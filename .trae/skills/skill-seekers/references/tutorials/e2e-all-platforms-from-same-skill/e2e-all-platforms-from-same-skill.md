# How To: E2E All Platforms From Same Skill

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that all platforms can package the same skill

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

### Step 1: 'Test that all platforms can package the same skill'

```python
'Test that all platforms can package the same skill'
```

### Step 2: Assign platforms = value

```python
platforms = ['claude', 'gemini', 'openai', 'markdown']
```

### Step 3: Assign packages = value

```python
packages = {}
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(packages), 4)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(str(packages['claude']).endswith('.zip'))
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(str(packages['gemini']).endswith('.tar.gz'))
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(str(packages['openai']).endswith('.zip'))
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(str(packages['markdown']).endswith('.zip'))
```

### Step 9: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 10: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(self.skill_dir, self.output_dir)
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(package_path.exists(), f'Package not created for {platform}')
```

### Step 12: Assign unknown = package_path

```python
packages[platform] = package_path
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
'Test that all platforms can package the same skill'
platforms = ['claude', 'gemini', 'openai', 'markdown']
packages = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    self.assertTrue(package_path.exists(), f'Package not created for {platform}')
    packages[platform] = package_path
self.assertEqual(len(packages), 4)
self.assertTrue(str(packages['claude']).endswith('.zip'))
self.assertTrue(str(packages['gemini']).endswith('.tar.gz'))
self.assertTrue(str(packages['openai']).endswith('.zip'))
self.assertTrue(str(packages['markdown']).endswith('.zip'))
```

## Next Steps


---

*Source: test_adaptors_e2e.py:129 | Complexity: Advanced | Last updated: 2026-02-14*