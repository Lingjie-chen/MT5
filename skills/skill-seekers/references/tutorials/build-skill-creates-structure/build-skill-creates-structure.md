# How To: Build Skill Creates Structure

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that build_skill creates required directory structure

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

### Step 1: 'Test that build_skill creates required directory structure'

```python
'Test that build_skill creates required directory structure'
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
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test content', 'code_blocks': [], 'images': []}], 'total_pages': 1}
```

### Step 6: Assign converter.categories = value

```python
converter.categories = {'getting_started': [converter.extracted_data['pages'][0]]}
```

### Step 7: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 8: Assign skill_dir = value

```python
skill_dir = Path(self.temp_dir) / 'test_skill'
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(skill_dir.exists())
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue((skill_dir / 'references').exists())
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue((skill_dir / 'scripts').exists())
```

### Step 12: Call self.assertTrue()

```python
self.assertTrue((skill_dir / 'assets').exists())
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
'Test that build_skill creates required directory structure'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test content', 'code_blocks': [], 'images': []}], 'total_pages': 1}
converter.categories = {'getting_started': [converter.extracted_data['pages'][0]]}
converter.build_skill()
skill_dir = Path(self.temp_dir) / 'test_skill'
self.assertTrue(skill_dir.exists())
self.assertTrue((skill_dir / 'references').exists())
self.assertTrue((skill_dir / 'scripts').exists())
self.assertTrue((skill_dir / 'assets').exists())
```

## Next Steps


---

*Source: test_pdf_scraper.py:173 | Complexity: Advanced | Last updated: 2026-02-14*