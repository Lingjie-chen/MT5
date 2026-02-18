# How To: Cache Overwrite

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test cache can be overwritten

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

### Step 1: 'Test cache can be overwritten'

```python
'Test cache can be overwritten'
```

### Step 2: Assign extractor = self.PDFExtractor.__new__(...)

```python
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
```

### Step 3: Assign extractor._cache = value

```python
extractor._cache = {}
```

### Step 4: Assign extractor.use_cache = True

```python
extractor.use_cache = True
```

### Step 5: Call extractor.set_cached()

```python
extractor.set_cached('page_1', {'version': 1})
```

### Step 6: Call extractor.set_cached()

```python
extractor.set_cached('page_1', {'version': 2})
```

### Step 7: Assign cached = extractor.get_cached(...)

```python
cached = extractor.get_cached('page_1')
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(cached['version'], 2)
```


## Complete Example

```python
# Workflow
'Test cache can be overwritten'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
extractor.set_cached('page_1', {'version': 1})
extractor.set_cached('page_1', {'version': 2})
cached = extractor.get_cached('page_1')
self.assertEqual(cached['version'], 2)
```

## Next Steps


---

*Source: test_pdf_advanced_features.py:380 | Complexity: Advanced | Last updated: 2026-02-14*