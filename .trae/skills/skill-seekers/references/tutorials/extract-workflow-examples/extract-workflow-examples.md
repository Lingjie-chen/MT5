# How To: Extract Workflow Examples

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test extraction of workflow examples from mixed examples

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

### Step 1: 'Test extraction of workflow examples from mixed examples'

```python
'Test extraction of workflow examples from mixed examples'
```

### Step 2: Assign examples = value

```python
examples = [{'category': 'workflow', 'code': 'db = Database()\nuser = User()\ndb.save(user)', 'test_name': 'test_user_workflow', 'file_path': 'tests/test_user.py', 'language': 'python'}, {'category': 'instantiation', 'code': 'db = Database()', 'test_name': 'test_db', 'file_path': 'tests/test_db.py', 'language': 'python'}]
```

### Step 3: Assign workflows = self.builder._extract_workflow_examples(...)

```python
workflows = self.builder._extract_workflow_examples(examples)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(workflows), 1)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(workflows[0]['category'], 'workflow')
```


## Complete Example

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test extraction of workflow examples from mixed examples'
examples = [{'category': 'workflow', 'code': 'db = Database()\nuser = User()\ndb.save(user)', 'test_name': 'test_user_workflow', 'file_path': 'tests/test_user.py', 'language': 'python'}, {'category': 'instantiation', 'code': 'db = Database()', 'test_name': 'test_db', 'file_path': 'tests/test_db.py', 'language': 'python'}]
workflows = self.builder._extract_workflow_examples(examples)
self.assertEqual(len(workflows), 1)
self.assertEqual(workflows[0]['category'], 'workflow')
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:427 | Complexity: Intermediate | Last updated: 2026-02-14*