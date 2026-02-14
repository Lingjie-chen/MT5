# How To: Creates Pdf Index With Count

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that PDF index shows correct document count.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `shutil`
- `tempfile`
- `unittest`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`

**Setup Required:**
```python
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)
```

## Step-by-Step Guide

### Step 1: 'Test that PDF index shows correct document count.'

```python
'Test that PDF index shows correct document count.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_pdf', 'description': 'Test', 'sources': []}
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': [], 'github': [], 'pdf': [{'path': '/path/to/doc1.pdf'}, {'path': '/path/to/doc2.pdf'}, {'path': '/path/to/doc3.pdf'}]}
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Call builder._generate_pdf_references()

```python
builder._generate_pdf_references(scraped_data['pdf'])
```

### Step 6: Assign pdf_index = os.path.join(...)

```python
pdf_index = os.path.join(builder.skill_dir, 'references', 'pdf', 'index.md')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(pdf_index))
```

### Step 8: Assign content = f.read(...)

```python
content = f.read()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('3 PDF document', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that PDF index shows correct document count.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_pdf', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [], 'pdf': [{'path': '/path/to/doc1.pdf'}, {'path': '/path/to/doc2.pdf'}, {'path': '/path/to/doc3.pdf'}]}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_pdf_references(scraped_data['pdf'])
pdf_index = os.path.join(builder.skill_dir, 'references', 'pdf', 'index.md')
self.assertTrue(os.path.exists(pdf_index))
with open(pdf_index) as f:
    content = f.read()
    self.assertIn('3 PDF document', content)
```

## Next Steps


---

*Source: test_multi_source.py:446 | Complexity: Advanced | Last updated: 2026-02-14*