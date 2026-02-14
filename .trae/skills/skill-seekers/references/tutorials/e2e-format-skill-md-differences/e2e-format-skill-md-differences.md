# How To: E2E Format Skill Md Differences

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that each platform formats SKILL.md differently

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

### Step 1: 'Test that each platform formats SKILL.md differently'

```python
'Test that each platform formats SKILL.md differently'
```

### Step 2: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='test-skill', description='Test skill for E2E testing')
```

### Step 3: Assign formats = value

```python
formats = {}
```

### Step 4: Call self.assertTrue()

```python
self.assertTrue(formats['claude'].startswith('---'))
```

### Step 5: Call self.assertFalse()

```python
self.assertFalse(formats['gemini'].startswith('---'))
```

### Step 6: Call self.assertFalse()

```python
self.assertFalse(formats['markdown'].startswith('---'))
```

### Step 7: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor(platform)
```

### Step 8: Assign formatted = adaptor.format_skill_md(...)

```python
formatted = adaptor.format_skill_md(self.skill_dir, metadata)
```

### Step 9: Assign unknown = formatted

```python
formats[platform] = formatted
```

### Step 10: Call self.assertIn()

```python
self.assertIn('react', formatted.lower(), f'{platform} should contain skill content')
```

### Step 11: Call self.assertGreater()

```python
self.assertGreater(len(formatted), 100, f'{platform} should have substantial content')
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
'Test that each platform formats SKILL.md differently'
metadata = SkillMetadata(name='test-skill', description='Test skill for E2E testing')
formats = {}
for platform in ['claude', 'gemini', 'openai', 'markdown']:
    adaptor = get_adaptor(platform)
    formatted = adaptor.format_skill_md(self.skill_dir, metadata)
    formats[platform] = formatted
self.assertTrue(formats['claude'].startswith('---'))
self.assertFalse(formats['gemini'].startswith('---'))
self.assertFalse(formats['markdown'].startswith('---'))
for platform, formatted in formats.items():
    self.assertIn('react', formatted.lower(), f'{platform} should contain skill content')
    self.assertGreater(len(formatted), 100, f'{platform} should have substantial content')
```

## Next Steps


---

*Source: test_adaptors_e2e.py:384 | Complexity: Advanced | Last updated: 2026-02-14*