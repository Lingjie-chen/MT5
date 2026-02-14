# How To: Build Skill Creates Skill Md

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that SKILL.md is created

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

### Step 1: 'Test that SKILL.md is created'

```python
'Test that SKILL.md is created'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_skill', 'pdf_path': 'test.pdf', 'description': 'Test description'}
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
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test', 'code_blocks': [], 'images': []}], 'total_pages': 1}
```

### Step 6: Assign converter.categories = value

```python
converter.categories = {'test': [converter.extracted_data['pages'][0]]}
```

### Step 7: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 8: Assign skill_md = value

```python
skill_md = Path(self.temp_dir) / 'test_skill' / 'SKILL.md'
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(skill_md.exists())
```

### Step 10: Assign content = skill_md.read_text(...)

```python
content = skill_md.read_text()
```

### Step 11: Call self.assertIn()

```python
self.assertIn('test_skill', content)
```

### Step 12: Call self.assertIn()

```python
self.assertIn('Test description', content)
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
'Test that SKILL.md is created'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf', 'description': 'Test description'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test', 'code_blocks': [], 'images': []}], 'total_pages': 1}
converter.categories = {'test': [converter.extracted_data['pages'][0]]}
converter.build_skill()
skill_md = Path(self.temp_dir) / 'test_skill' / 'SKILL.md'
self.assertTrue(skill_md.exists())
content = skill_md.read_text()
self.assertIn('test_skill', content)
self.assertIn('Test description', content)
```

## Next Steps


---

*Source: test_pdf_scraper.py:199 | Complexity: Advanced | Last updated: 2026-02-14*