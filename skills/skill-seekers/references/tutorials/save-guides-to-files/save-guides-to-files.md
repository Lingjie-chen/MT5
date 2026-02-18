# How To: Save Guides To Files

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test saving guides to markdown files

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

### Step 1: 'Test saving guides to markdown files'

```python
'Test saving guides to markdown files'
```

### Step 2: Assign guides = value

```python
guides = [HowToGuide(guide_id='test-guide', title='Test Guide', overview='Test overview', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Test step')])]
```

### Step 3: Assign collection = GuideCollection(...)

```python
collection = GuideCollection(total_guides=1, guides=guides, guides_by_complexity={'beginner': 1}, guides_by_use_case={})
```

### Step 4: Assign output_dir = Path(...)

```python
output_dir = Path(self.temp_dir)
```

### Step 5: Call self.builder._save_guides_to_files()

```python
self.builder._save_guides_to_files(collection, output_dir)
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue((output_dir / 'index.md').exists())
```

### Step 7: Assign index_content = unknown.read_text(...)

```python
index_content = (output_dir / 'index.md').read_text()
```

### Step 8: Call self.assertIn()

```python
self.assertIn('Test Guide', index_content)
```

### Step 9: Assign md_files = list(...)

```python
md_files = list(output_dir.glob('*.md'))
```

### Step 10: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(md_files), 1)
```


## Complete Example

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test saving guides to markdown files'
guides = [HowToGuide(guide_id='test-guide', title='Test Guide', overview='Test overview', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Test step')])]
collection = GuideCollection(total_guides=1, guides=guides, guides_by_complexity={'beginner': 1}, guides_by_use_case={})
output_dir = Path(self.temp_dir)
self.builder._save_guides_to_files(collection, output_dir)
self.assertTrue((output_dir / 'index.md').exists())
index_content = (output_dir / 'index.md').read_text()
self.assertIn('Test Guide', index_content)
md_files = list(output_dir.glob('*.md'))
self.assertGreaterEqual(len(md_files), 1)
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:490 | Complexity: Advanced | Last updated: 2026-02-14*