# How To: Build With Ai Enhancement Disabled

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test building guides WITHOUT AI enhancement (backward compatibility)

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
self.temp_dir = tempfile.mkdtemp()
```

## Step-by-Step Guide

### Step 1: 'Test building guides WITHOUT AI enhancement (backward compatibility)'

```python
'Test building guides WITHOUT AI enhancement (backward compatibility)'
```

### Step 2: Assign examples = value

```python
examples = [{'example_id': 'test_001', 'test_name': 'test_user_registration', 'category': 'workflow', 'code': '\ndef test_user_registration():\n    user = User.create(username="test", email="test@example.com")\n    assert user.id is not None\n    assert user.is_active is True\n                ', 'language': 'python', 'file_path': 'tests/test_user.py', 'line_start': 10, 'tags': ['authentication', 'user'], 'ai_analysis': {'tutorial_group': 'User Management', 'best_practices': ['Validate email format'], 'common_mistakes': ['Not checking uniqueness']}}]
```

### Step 3: Assign builder = HowToGuideBuilder(...)

```python
builder = HowToGuideBuilder()
```

### Step 4: Assign output_dir = value

```python
output_dir = Path(self.temp_dir) / 'guides'
```

### Step 5: Assign collection = builder.build_guides_from_examples(...)

```python
collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=False, ai_mode='none')
```

### Step 6: Call self.assertIsInstance()

```python
self.assertIsInstance(collection, GuideCollection)
```

### Step 7: Call self.assertGreater()

```python
self.assertGreater(collection.total_guides, 0)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(output_dir.exists())
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue((output_dir / 'index.md').exists())
```


## Complete Example

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test building guides WITHOUT AI enhancement (backward compatibility)'
examples = [{'example_id': 'test_001', 'test_name': 'test_user_registration', 'category': 'workflow', 'code': '\ndef test_user_registration():\n    user = User.create(username="test", email="test@example.com")\n    assert user.id is not None\n    assert user.is_active is True\n                ', 'language': 'python', 'file_path': 'tests/test_user.py', 'line_start': 10, 'tags': ['authentication', 'user'], 'ai_analysis': {'tutorial_group': 'User Management', 'best_practices': ['Validate email format'], 'common_mistakes': ['Not checking uniqueness']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides'
collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=False, ai_mode='none')
self.assertIsInstance(collection, GuideCollection)
self.assertGreater(collection.total_guides, 0)
self.assertTrue(output_dir.exists())
self.assertTrue((output_dir / 'index.md').exists())
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:653 | Complexity: Advanced | Last updated: 2026-02-14*