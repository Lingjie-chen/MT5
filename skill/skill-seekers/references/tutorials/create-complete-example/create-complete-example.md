# How To: Create Complete Example

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete example generation

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
self.generator = GuideGenerator()
```

## Step-by-Step Guide

### Step 1: 'Test complete example generation'

```python
'Test complete example generation'
```

### Step 2: Assign guide = HowToGuide(...)

```python
guide = HowToGuide(guide_id='test-1', title='Test', overview='Test', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Assign'), WorkflowStep(2, 'print(x)', 'Print')], workflows=[{'code': 'x = 1\nprint(x)', 'language': 'python'}])
```

### Step 3: Assign example_md = self.generator._create_complete_example(...)

```python
example_md = self.generator._create_complete_example(guide)
```

### Step 4: Call self.assertIn()

```python
self.assertIn('## Complete Example', example_md)
```

### Step 5: Call self.assertIn()

```python
self.assertIn('```python', example_md)
```


## Complete Example

```python
# Setup
self.generator = GuideGenerator()

# Workflow
'Test complete example generation'
guide = HowToGuide(guide_id='test-1', title='Test', overview='Test', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Assign'), WorkflowStep(2, 'print(x)', 'Print')], workflows=[{'code': 'x = 1\nprint(x)', 'language': 'python'}])
example_md = self.generator._create_complete_example(guide)
self.assertIn('## Complete Example', example_md)
self.assertIn('```python', example_md)
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:373 | Complexity: Intermediate | Last updated: 2026-02-14*