# How To: Image References In Markdown

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that images are referenced in markdown files

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

### Step 1: 'Test that images are referenced in markdown files'

```python
'Test that images are referenced in markdown files'
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

### Step 5: Assign mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

```python
mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
```

### Step 6: Assign converter.extracted_data = value

```python
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Architecture diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 200, 'height': 150, 'data': mock_image_bytes}]}], 'total_pages': 1}
```

### Step 7: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 8: Assign ref_file = value

```python
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
```

### Step 9: Assign content = ref_file.read_text(...)

```python
content = ref_file.read_text()
```

### Step 10: Call self.assertIn()

```python
self.assertIn('![', content)
```

### Step 11: Call self.assertIn()

```python
self.assertIn('../assets/', content)
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
'Test that images are referenced in markdown files'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Architecture diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 200, 'height': 150, 'data': mock_image_bytes}]}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('![', content)
self.assertIn('../assets/', content)
```

## Next Steps


---

*Source: test_pdf_scraper.py:391 | Complexity: Advanced | Last updated: 2026-02-14*