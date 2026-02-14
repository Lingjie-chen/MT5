# How To: Detect Csharp From Namespace

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test C# detection from 'namespace' keyword

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `bs4`
- `skill_seekers.cli.doc_scraper`

**Setup Required:**
```python
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)
```

## Step-by-Step Guide

### Step 1: "Test C# detection from 'namespace' keyword"

```python
"Test C# detection from 'namespace' keyword"
```

### Step 2: Assign html = '<code>namespace MyNamespace\n{\n    public class Test { }\n}</code>'

```python
html = '<code>namespace MyNamespace\n{\n    public class Test { }\n}</code>'
```

### Step 3: Assign elem = BeautifulSoup.find(...)

```python
elem = BeautifulSoup(html, 'html.parser').find('code')
```

### Step 4: Assign code = elem.get_text(...)

```python
code = elem.get_text()
```

### Step 5: Assign lang = self.converter.detect_language(...)

```python
lang = self.converter.detect_language(elem, code)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(lang, 'csharp', 'Should detect C# from namespace')
```


## Complete Example

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

# Workflow
"Test C# detection from 'namespace' keyword"
html = '<code>namespace MyNamespace\n{\n    public class Test { }\n}</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'csharp', 'Should detect C# from namespace')
```

## Next Steps


---

*Source: test_scraper_features.py:196 | Complexity: Intermediate | Last updated: 2026-02-14*