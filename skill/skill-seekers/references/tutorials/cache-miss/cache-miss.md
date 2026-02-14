# How To: Cache Miss

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test cache miss returns None

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

### Step 1: 'Test cache miss returns None'

```python
'Test cache miss returns None'
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

### Step 5: Assign cached = extractor.get_cached(...)

```python
cached = extractor.get_cached('nonexistent_key')
```

### Step 6: Call self.assertIsNone()

```python
self.assertIsNone(cached)
```


## Complete Example

```python
# Workflow
'Test cache miss returns None'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
cached = extractor.get_cached('nonexistent_key')
self.assertIsNone(cached)
```

## Next Steps


---

*Source: test_pdf_advanced_features.py:354 | Complexity: Intermediate | Last updated: 2026-02-14*