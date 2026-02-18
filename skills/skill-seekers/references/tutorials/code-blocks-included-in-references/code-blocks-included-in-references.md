# How To: Code Blocks Included In References

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that code blocks are included in reference files

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

### Step 1: 'Test that code blocks are included in reference files'

```python
'Test that code blocks are included in reference files'
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
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Example code', 'code_blocks': [{'code': "def hello():\n    print('world')", 'language': 'python', 'quality': 8.0}], 'images': []}], 'total_pages': 1}
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
self.assertIn('```python', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('def hello()', content)
```

### Step 11: Call self.assertIn()

```python
self.assertIn("print('world')", content)
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
'Test that code blocks are included in reference files'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Example code', 'code_blocks': [{'code': "def hello():\n    print('world')", 'language': 'python', 'quality': 8.0}], 'images': []}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('```python', content)
self.assertIn('def hello()', content)
self.assertIn("print('world')", content)
```

## Next Steps


---

*Source: test_pdf_scraper.py:262 | Complexity: Advanced | Last updated: 2026-02-14*