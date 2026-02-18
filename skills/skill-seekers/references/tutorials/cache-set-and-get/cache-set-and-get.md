# How To: Cache Set And Get

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test setting and getting cached values

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

### Step 1: 'Test setting and getting cached values'

```python
'Test setting and getting cached values'
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

### Step 5: Assign test_data = value

```python
test_data = {'page': 1, 'text': 'cached content'}
```

### Step 6: Call extractor.set_cached()

```python
extractor.set_cached('page_1', test_data)
```

### Step 7: Assign cached = extractor.get_cached(...)

```python
cached = extractor.get_cached('page_1')
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(cached, test_data)
```


## Complete Example

```python
# Workflow
'Test setting and getting cached values'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
test_data = {'page': 1, 'text': 'cached content'}
extractor.set_cached('page_1', test_data)
cached = extractor.get_cached('page_1')
self.assertEqual(cached, test_data)
```

## Next Steps


---

*Source: test_pdf_advanced_features.py:339 | Complexity: Advanced | Last updated: 2026-02-14*