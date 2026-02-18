# How To: Categorize By Keywords

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test categorization using keyword matching

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `shutil`
- `tempfile`
- `unittest`
- `pathlib`
- `fitz`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`
- `skill_seekers.cli.pdf_scraper`

**Setup Required:**
```python
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()
```

## Step-by-Step Guide

### Step 1: 'Test categorization using keyword matching'

```python
'Test categorization using keyword matching'
```

### Step 2: Assign config = value

```python
config = {'name': 'test', 'pdf_path': 'test.pdf', 'categories': {'getting_started': ['introduction', 'getting started'], 'api': ['api', 'reference', 'function']}}
```

### Step 3: Assign converter = self.PDFToSkillConverter(...)

```python
converter = self.PDFToSkillConverter(config)
```

### Step 4: Assign converter.extracted_data = value

```python
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Introduction to the API', 'chapter': 'Chapter 1: Getting Started'}, {'page_number': 2, 'text': 'API reference for functions', 'chapter': None}]}
```

### Step 5: Assign categories = converter.categorize_content(...)

```python
categories = converter.categorize_content()
```

### Step 6: Call self.assertIn()

```python
self.assertIn('test', categories)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(len(categories), 1)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(len(categories['test']['pages']), 2)
```


## Complete Example

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test categorization using keyword matching'
config = {'name': 'test', 'pdf_path': 'test.pdf', 'categories': {'getting_started': ['introduction', 'getting started'], 'api': ['api', 'reference', 'function']}}
converter = self.PDFToSkillConverter(config)
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Introduction to the API', 'chapter': 'Chapter 1: Getting Started'}, {'page_number': 2, 'text': 'API reference for functions', 'chapter': None}]}
categories = converter.categorize_content()
self.assertIn('test', categories)
self.assertEqual(len(categories), 1)
self.assertEqual(len(categories['test']['pages']), 2)
```

## Next Steps


---

*Source: test_pdf_scraper.py:90 | Complexity: Advanced | Last updated: 2026-02-14*