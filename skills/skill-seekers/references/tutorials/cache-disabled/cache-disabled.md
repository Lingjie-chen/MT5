# How To: Cache Disabled

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test caching can be disabled

## Prerequisites

**Required Modules:**
- `io`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `unittest.mock`
- `fitz`
- `pytesseract`
- `PIL`
- `pdf_extractor_poc`
- `pdf_extractor_poc`
- `pdf_extractor_poc`
- `pdf_extractor_poc`
- `pdf_extractor_poc`
- `os`
- `pdf_extractor_poc`


## Step-by-Step Guide

### Step 1: 'Test caching can be disabled'

```python
'Test caching can be disabled'
```

### Step 2: Assign extractor = self.PDFExtractor.__new__(...)

```python
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
```

### Step 3: Assign extractor._cache = value

```python
extractor._cache = {}
```

### Step 4: Assign extractor.use_cache = False

```python
extractor.use_cache = False
```

### Step 5: Call extractor.set_cached()

```python
extractor.set_cached('page_1', {'data': 'test'})
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(len(extractor._cache), 0)
```

### Step 7: Assign cached = extractor.get_cached(...)

```python
cached = extractor.get_cached('page_1')
```

### Step 8: Call self.assertIsNone()

```python
self.assertIsNone(cached)
```


## Complete Example

```python
# Workflow
'Test caching can be disabled'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = False
extractor.set_cached('page_1', {'data': 'test'})
self.assertEqual(len(extractor._cache), 0)
cached = extractor.get_cached('page_1')
self.assertIsNone(cached)
```

## Next Steps


---

*Source: test_pdf_advanced_features.py:364 | Complexity: Advanced | Last updated: 2026-02-14*