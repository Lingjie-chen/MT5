# How To: No Duplicate Directories Created

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that source directories are cleaned up after copying to references/ (Issue #279).

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

### Step 1: 'Test that source directories are cleaned up after copying to references/ (Issue #279).'

```python
'Test that source directories are cleaned up after copying to references/ (Issue #279).'
```

### Step 2: Assign test_dirs = value

```python
test_dirs = ['documentation', 'api_reference', 'patterns']
```

### Step 3: Call _generate_references()

```python
_generate_references(self.output_dir)
```

### Step 4: Assign references_dir = value

```python
references_dir = self.output_dir / 'references'
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(references_dir.exists(), 'references/ should exist')
```

### Step 6: Assign dir_path = value

```python
dir_path = self.output_dir / dir_name
```

### Step 7: Call dir_path.mkdir()

```python
dir_path.mkdir()
```

### Step 8: Call unknown.write_text()

```python
(dir_path / 'test.txt').write_text(f'Test content for {dir_name}')
```

### Step 9: Assign ref_path = value

```python
ref_path = references_dir / dir_name
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(ref_path.exists(), f'references/{dir_name} should exist')
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue((ref_path / 'test.txt').exists(), f'references/{dir_name}/test.txt should exist')
```

### Step 12: Assign source_path = value

```python
source_path = self.output_dir / dir_name
```

### Step 13: Call self.assertFalse()

```python
self.assertFalse(source_path.exists(), f'Source directory {dir_name}/ should be cleaned up to avoid duplication')
```


## Complete Example

```python
# Workflow
'Test that source directories are cleaned up after copying to references/ (Issue #279).'
test_dirs = ['documentation', 'api_reference', 'patterns']
for dir_name in test_dirs:
    dir_path = self.output_dir / dir_name
    dir_path.mkdir()
    (dir_path / 'test.txt').write_text(f'Test content for {dir_name}')
_generate_references(self.output_dir)
references_dir = self.output_dir / 'references'
self.assertTrue(references_dir.exists(), 'references/ should exist')
for dir_name in test_dirs:
    ref_path = references_dir / dir_name
    self.assertTrue(ref_path.exists(), f'references/{dir_name} should exist')
    self.assertTrue((ref_path / 'test.txt').exists(), f'references/{dir_name}/test.txt should exist')
for dir_name in test_dirs:
    source_path = self.output_dir / dir_name
    self.assertFalse(source_path.exists(), f'Source directory {dir_name}/ should be cleaned up to avoid duplication')
```

## Next Steps


---

*Source: test_codebase_scraper.py:411 | Complexity: Advanced | Last updated: 2026-02-14*