# How To: E2E Package Filename Convention

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that package filenames follow convention

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

### Step 1: 'Test that package filenames follow convention'

```python
'Test that package filenames follow convention'
```

### Step 2: Assign test_cases = value

```python
test_cases = [('claude', 'test-skill.zip'), ('gemini', 'test-skill-gemini.tar.gz'), ('openai', 'test-skill-openai.zip'), ('markdown', 'test-skill-markdown.zip')]
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
self.assertEqual(package_path.name, expected_name, f'{platform} package filename incorrect')
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
'Test that package filenames follow convention'
test_cases = [('claude', 'test-skill.zip'), ('gemini', 'test-skill-gemini.tar.gz'), ('openai', 'test-skill-openai.zip'), ('markdown', 'test-skill-markdown.zip')]
for platform, expected_name in test_cases:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    self.assertEqual(package_path.name, expected_name, f'{platform} package filename incorrect')
```

## Next Steps


---

*Source: test_adaptors_e2e.py:306 | Complexity: Intermediate | Last updated: 2026-02-14*