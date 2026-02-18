# How To: Build Skill Creates Reference Files

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that reference files are created for categories

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

### Step 1: 'Test that reference files are created for categories'

```python
'Test that reference files are created for categories'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
```

### Step 3: Assign converter = self.PDFToSkillConverter(...)

```python
converter = self.PDFToSkillConverter(config)
```

### Step 4: Assign converter.skill_dir = str(...)

```python
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
```

### Step 5: Assign converter.extracted_data = value

```python
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Getting started', 'code_blocks': [], 'images': []}, {'page_number': 2, 'text': 'API reference', 'code_blocks': [], 'images': []}], 'total_pages': 2}
```

### Step 6: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 7: Assign refs_dir = value

```python
refs_dir = Path(self.temp_dir) / 'test_skill' / 'references'
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue((refs_dir / 'test.md').exists())
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue((refs_dir / 'index.md').exists())
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
'Test that reference files are created for categories'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Getting started', 'code_blocks': [], 'images': []}, {'page_number': 2, 'text': 'API reference', 'code_blocks': [], 'images': []}], 'total_pages': 2}
converter.build_skill()
refs_dir = Path(self.temp_dir) / 'test_skill' / 'references'
self.assertTrue((refs_dir / 'test.md').exists())
self.assertTrue((refs_dir / 'index.md').exists())
```

## Next Steps


---

*Source: test_pdf_scraper.py:223 | Complexity: Advanced | Last updated: 2026-02-14*