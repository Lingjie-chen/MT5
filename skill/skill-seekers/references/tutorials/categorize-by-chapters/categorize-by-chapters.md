# How To: Categorize By Chapters

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test categorization using chapter information

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

### Step 1: 'Test categorization using chapter information'

```python
'Test categorization using chapter information'
```

### Step 2: Assign config = value

```python
config = {'name': 'test', 'pdf_path': 'test.pdf'}
```

### Step 3: Assign converter = self.PDFToSkillConverter(...)

```python
converter = self.PDFToSkillConverter(config)
```

### Step 4: Assign converter.extracted_data = value

```python
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Content here', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 2, 'text': 'More content', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 3, 'text': 'New chapter', 'chapter': 'Chapter 2: Advanced Topics'}]}
```

### Step 5: Assign categories = converter.categorize_content(...)

```python
categories = converter.categorize_content()
```

### Step 6: Call self.assertIsInstance()

```python
self.assertIsInstance(categories, dict)
```

### Step 7: Call self.assertGreater()

```python
self.assertGreater(len(categories), 0)
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
'Test categorization using chapter information'
config = {'name': 'test', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Content here', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 2, 'text': 'More content', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 3, 'text': 'New chapter', 'chapter': 'Chapter 2: Advanced Topics'}]}
categories = converter.categorize_content()
self.assertIsInstance(categories, dict)
self.assertGreater(len(categories), 0)
```

## Next Steps


---

*Source: test_pdf_scraper.py:123 | Complexity: Intermediate | Last updated: 2026-02-14*