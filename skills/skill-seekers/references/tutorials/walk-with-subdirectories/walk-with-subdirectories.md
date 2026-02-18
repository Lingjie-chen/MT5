# How To: Walk With Subdirectories

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test walking nested directory structure.

## Prerequisites

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.codebase_scraper`


## Step-by-Step Guide

### Step 1: 'Test walking nested directory structure.'

```python
'Test walking nested directory structure.'
```

### Step 2: Assign src_dir = value

```python
src_dir = self.root / 'src'
```

### Step 3: Call src_dir.mkdir()

```python
src_dir.mkdir()
```

### Step 4: Call unknown.write_text()

```python
(src_dir / 'module.py').write_text('test')
```

### Step 5: Assign tests_dir = value

```python
tests_dir = self.root / 'tests'
```

### Step 6: Call tests_dir.mkdir()

```python
tests_dir.mkdir()
```

### Step 7: Call unknown.write_text()

```python
(tests_dir / 'test_module.py').write_text('test')
```

### Step 8: Assign files = walk_directory(...)

```python
files = walk_directory(self.root)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(len(files), 2)
```

### Step 10: Assign filenames = value

```python
filenames = [f.name for f in files]
```

### Step 11: Call self.assertIn()

```python
self.assertIn('module.py', filenames)
```

### Step 12: Call self.assertIn()

```python
self.assertIn('test_module.py', filenames)
```


## Complete Example

```python
# Workflow
'Test walking nested directory structure.'
src_dir = self.root / 'src'
src_dir.mkdir()
(src_dir / 'module.py').write_text('test')
tests_dir = self.root / 'tests'
tests_dir.mkdir()
(tests_dir / 'test_module.py').write_text('test')
files = walk_directory(self.root)
self.assertEqual(len(files), 2)
filenames = [f.name for f in files]
self.assertIn('module.py', filenames)
self.assertIn('test_module.py', filenames)
```

## Next Steps


---

*Source: test_codebase_scraper.py:159 | Complexity: Advanced | Last updated: 2026-02-14*