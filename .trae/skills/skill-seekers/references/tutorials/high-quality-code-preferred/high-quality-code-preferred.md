# How To: High Quality Code Preferred

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that high-quality code blocks are prioritized

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

### Step 1: 'Test that high-quality code blocks are prioritized'

```python
'Test that high-quality code blocks are prioritized'
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
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Code examples', 'code_blocks': [{'code': 'x = 1', 'language': 'python', 'quality': 2.0}, {'code': 'def process():\n    return result', 'language': 'python', 'quality': 9.0}], 'images': []}], 'total_pages': 1}
```

### Step 6: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 7: Assign ref_file = value

```python
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
```

### Step 8: Assign content = ref_file.read_text(...)

```python
content = ref_file.read_text()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('def process()', content)
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
'Test that high-quality code blocks are prioritized'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Code examples', 'code_blocks': [{'code': 'x = 1', 'language': 'python', 'quality': 2.0}, {'code': 'def process():\n    return result', 'language': 'python', 'quality': 9.0}], 'images': []}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('def process()', content)
```

## Next Steps


---

*Source: test_pdf_scraper.py:300 | Complexity: Advanced | Last updated: 2026-02-14*