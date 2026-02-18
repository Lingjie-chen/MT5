# How To: Images Saved To Assets

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that images are saved to assets directory

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

### Step 1: 'Test that images are saved to assets directory'

```python
'Test that images are saved to assets directory'
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
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'See diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 100, 'height': 100, 'data': mock_image_bytes}]}], 'total_pages': 1}
```

### Step 7: Assign converter.categories = value

```python
converter.categories = {'diagrams': [converter.extracted_data['pages'][0]]}
```

### Step 8: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 9: Assign assets_dir = value

```python
assets_dir = Path(self.temp_dir) / 'test_skill' / 'assets'
```

### Step 10: Assign image_files = list(...)

```python
image_files = list(assets_dir.glob('*.png'))
```

### Step 11: Call self.assertGreater()

```python
self.assertGreater(len(image_files), 0)
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
'Test that images are saved to assets directory'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'See diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 100, 'height': 100, 'data': mock_image_bytes}]}], 'total_pages': 1}
converter.categories = {'diagrams': [converter.extracted_data['pages'][0]]}
converter.build_skill()
assets_dir = Path(self.temp_dir) / 'test_skill' / 'assets'
image_files = list(assets_dir.glob('*.png'))
self.assertGreater(len(image_files), 0)
```

## Next Steps


---

*Source: test_pdf_scraper.py:352 | Complexity: Advanced | Last updated: 2026-02-14*