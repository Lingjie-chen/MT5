# How To: Analyze Python Workflow

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test analysis of Python workflow with multiple steps

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
self.analyzer = WorkflowAnalyzer()
```

## Step-by-Step Guide

### Step 1: 'Test analysis of Python workflow with multiple steps'

```python
'Test analysis of Python workflow with multiple steps'
```

### Step 2: Assign workflow = value

```python
workflow = {'code': "\ndef test_user_creation_workflow():\n    # Step 1: Create database\n    db = Database('test.db')\n\n    # Step 2: Create user\n    user = User(name='Alice', email='alice@example.com')\n    db.save(user)\n\n    # Step 3: Verify creation\n    assert db.get_user('Alice').email == 'alice@example.com'\n", 'language': 'python', 'category': 'workflow', 'test_name': 'test_user_creation_workflow', 'file_path': 'tests/test_user.py'}
```

### Step 3: Assign unknown = self.analyzer.analyze_workflow(...)

```python
steps, metadata = self.analyzer.analyze_workflow(workflow)
```

### Step 4: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(steps), 2)
```

### Step 5: Call self.assertIsInstance()

```python
self.assertIsInstance(steps[0], WorkflowStep)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(steps[0].step_number, 1)
```

### Step 7: Call self.assertIsNotNone()

```python
self.assertIsNotNone(steps[0].description)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('complexity_level', metadata)
```

### Step 9: Call self.assertIn()

```python
self.assertIn(metadata['complexity_level'], ['beginner', 'intermediate', 'advanced'])
```


## Complete Example

```python
# Setup
self.analyzer = WorkflowAnalyzer()

# Workflow
'Test analysis of Python workflow with multiple steps'
workflow = {'code': "\ndef test_user_creation_workflow():\n    # Step 1: Create database\n    db = Database('test.db')\n\n    # Step 2: Create user\n    user = User(name='Alice', email='alice@example.com')\n    db.save(user)\n\n    # Step 3: Verify creation\n    assert db.get_user('Alice').email == 'alice@example.com'\n", 'language': 'python', 'category': 'workflow', 'test_name': 'test_user_creation_workflow', 'file_path': 'tests/test_user.py'}
steps, metadata = self.analyzer.analyze_workflow(workflow)
self.assertGreaterEqual(len(steps), 2)
self.assertIsInstance(steps[0], WorkflowStep)
self.assertEqual(steps[0].step_number, 1)
self.assertIsNotNone(steps[0].description)
self.assertIn('complexity_level', metadata)
self.assertIn(metadata['complexity_level'], ['beginner', 'intermediate', 'advanced'])
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:42 | Complexity: Advanced | Last updated: 2026-02-14*