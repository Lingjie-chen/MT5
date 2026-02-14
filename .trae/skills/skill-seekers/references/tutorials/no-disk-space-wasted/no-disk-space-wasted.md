# How To: No Disk Space Wasted

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that disk space is not wasted by duplicate directories.

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

### Step 1: 'Test that disk space is not wasted by duplicate directories.'

```python
'Test that disk space is not wasted by duplicate directories.'
```

### Step 2: Assign doc_dir = value

```python
doc_dir = self.output_dir / 'documentation'
```

### Step 3: Call doc_dir.mkdir()

```python
doc_dir.mkdir()
```

### Step 4: Assign test_content = value

```python
test_content = 'x' * 1000
```

### Step 5: Call unknown.write_text()

```python
(doc_dir / 'large_file.txt').write_text(test_content)
```

### Step 6: Call _generate_references()

```python
_generate_references(self.output_dir)
```

### Step 7: Assign ref_doc_dir = value

```python
ref_doc_dir = self.output_dir / 'references' / 'documentation'
```

### Step 8: Assign source_doc_dir = value

```python
source_doc_dir = self.output_dir / 'documentation'
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(ref_doc_dir.exists(), 'references/documentation/ should exist')
```

### Step 10: Call self.assertFalse()

```python
self.assertFalse(source_doc_dir.exists(), 'Source documentation/ should not exist (cleaned up)')
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue((ref_doc_dir / 'large_file.txt').exists(), 'File should exist in references/')
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')
```


## Complete Example

```python
# Workflow
'Test that disk space is not wasted by duplicate directories.'
doc_dir = self.output_dir / 'documentation'
doc_dir.mkdir()
test_content = 'x' * 1000
(doc_dir / 'large_file.txt').write_text(test_content)
_generate_references(self.output_dir)
ref_doc_dir = self.output_dir / 'references' / 'documentation'
source_doc_dir = self.output_dir / 'documentation'
self.assertTrue(ref_doc_dir.exists(), 'references/documentation/ should exist')
self.assertFalse(source_doc_dir.exists(), 'Source documentation/ should not exist (cleaned up)')
self.assertTrue((ref_doc_dir / 'large_file.txt').exists(), 'File should exist in references/')
self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')
```

## Next Steps


---

*Source: test_codebase_scraper.py:445 | Complexity: Advanced | Last updated: 2026-02-14*