# How To: Create Guide From Workflows

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test guide creation from grouped workflows

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.guide_enhancer`
- `skill_seekers.cli.how_to_guide_builder`
- `unittest.mock`
- `unittest.mock`
- `unittest.mock`
- `unittest.mock`
- `ast`
- `ast`

**Setup Required:**
```python
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()
```

## Step-by-Step Guide

### Step 1: 'Test guide creation from grouped workflows'

```python
'Test guide creation from grouped workflows'
```

### Step 2: Assign workflows = value

```python
workflows = [{'code': 'user = User(name="Alice")\ndb.save(user)', 'test_name': 'test_create_user', 'file_path': 'tests/test_user.py', 'language': 'python', 'category': 'workflow'}]
```

### Step 3: Assign guide = self.builder._create_guide(...)

```python
guide = self.builder._create_guide('User Management', workflows)
```

### Step 4: Call self.assertIsInstance()

```python
self.assertIsInstance(guide, HowToGuide)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(guide.title, 'User Management')
```

### Step 6: Call self.assertGreater()

```python
self.assertGreater(len(guide.steps), 0)
```

### Step 7: Call self.assertIn()

```python
self.assertIn(guide.complexity_level, ['beginner', 'intermediate', 'advanced'])
```


## Complete Example

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test guide creation from grouped workflows'
workflows = [{'code': 'user = User(name="Alice")\ndb.save(user)', 'test_name': 'test_create_user', 'file_path': 'tests/test_user.py', 'language': 'python', 'category': 'workflow'}]
guide = self.builder._create_guide('User Management', workflows)
self.assertIsInstance(guide, HowToGuide)
self.assertEqual(guide.title, 'User Management')
self.assertGreater(len(guide.steps), 0)
self.assertIn(guide.complexity_level, ['beginner', 'intermediate', 'advanced'])
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:452 | Complexity: Intermediate | Last updated: 2026-02-14*