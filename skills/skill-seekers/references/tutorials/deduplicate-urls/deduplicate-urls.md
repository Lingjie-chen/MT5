# How To: Deduplicate Urls

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that duplicate URLs are removed.

## Prerequisites

**Required Modules:**
- `os`
- `shutil`
- `unittest`
- `skill_seekers.cli.doc_scraper`
- `skill_seekers.cli.doc_scraper`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.llms_txt_parser`
- `skill_seekers.cli.doc_scraper`


## Step-by-Step Guide

### Step 1: 'Test that duplicate URLs are removed.'

```python
'Test that duplicate URLs are removed.'
```

### Step 2: Assign content = '\n- [Doc 1](https://example.com/doc.md)\n- [Doc 2](https://example.com/doc.md)\nhttps://example.com/doc.md\n'

```python
content = '\n- [Doc 1](https://example.com/doc.md)\n- [Doc 2](https://example.com/doc.md)\nhttps://example.com/doc.md\n'
```

### Step 3: Assign parser = LlmsTxtParser(...)

```python
parser = LlmsTxtParser(content)
```

### Step 4: Assign urls = parser.extract_urls(...)

```python
urls = parser.extract_urls()
```

### Step 5: Assign count = sum(...)

```python
count = sum((1 for u in urls if u == 'https://example.com/doc.md'))
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(count, 1)
```


## Complete Example

```python
# Workflow
'Test that duplicate URLs are removed.'
from skill_seekers.cli.llms_txt_parser import LlmsTxtParser
content = '\n- [Doc 1](https://example.com/doc.md)\n- [Doc 2](https://example.com/doc.md)\nhttps://example.com/doc.md\n'
parser = LlmsTxtParser(content)
urls = parser.extract_urls()
count = sum((1 for u in urls if u == 'https://example.com/doc.md'))
self.assertEqual(count, 1)
```

## Next Steps


---

*Source: test_markdown_parsing.py:273 | Complexity: Intermediate | Last updated: 2026-02-14*