# How To: E2E Package Format Validation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that each platform creates correct package format

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

### Step 1: 'Test that each platform creates correct package format'

```python
'Test that each platform creates correct package format'
```

### Step 2: Assign test_cases = value

```python
test_cases = [('claude', '.zip'), ('gemini', '.tar.gz'), ('openai', '.zip'), ('markdown', '.zip')]
```

### Step 3: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(self.skill_dir, self.output_dir)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(str(package_path).endswith('.tar.gz'), f'{platform} should create .tar.gz file')
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(str(package_path).endswith('.zip'), f'{platform} should create .zip file')
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
'Test that each platform creates correct package format'
test_cases = [('claude', '.zip'), ('gemini', '.tar.gz'), ('openai', '.zip'), ('markdown', '.zip')]
for platform, expected_ext in test_cases:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if expected_ext == '.tar.gz':
        self.assertTrue(str(package_path).endswith('.tar.gz'), f'{platform} should create .tar.gz file')
    else:
        self.assertTrue(str(package_path).endswith('.zip'), f'{platform} should create .zip file')
```

## Next Steps


---

*Source: test_adaptors_e2e.py:283 | Complexity: Intermediate | Last updated: 2026-02-14*