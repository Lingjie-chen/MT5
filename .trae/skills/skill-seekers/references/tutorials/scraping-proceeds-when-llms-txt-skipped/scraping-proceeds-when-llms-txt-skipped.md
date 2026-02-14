# How To: Scraping Proceeds When Llms Txt Skipped

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that HTML scraping proceeds normally when llms.txt is skipped.

## Prerequisites

**Required Modules:**
- `os`
- `tempfile`
- `unittest`
- `unittest.mock`
- `skill_seekers.cli.doc_scraper`

**Required Fixtures:**
- `api_client` fixture


## Step-by-Step Guide

### Step 1: 'Test that HTML scraping proceeds normally when llms.txt is skipped.'

```python
'Test that HTML scraping proceeds normally when llms.txt is skipped.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'skip_llms_txt': True}
```

### Step 3: Assign original_cwd = os.getcwd(...)

```python
original_cwd = os.getcwd()
```

### Step 4: Call os.chdir()

```python
os.chdir(tmpdir)
```

### Step 5: Assign converter = DocToSkillConverter(...)

```python
converter = DocToSkillConverter(config, dry_run=False)
```

### Step 6: Assign scrape_called = value

```python
scrape_called = []
```

### Step 7: Call os.chdir()

```python
os.chdir(original_cwd)
```

### Step 8: Call scrape_called.append()

```python
scrape_called.append(url)
```

### Step 9: Call converter.scrape_all()

```python
converter.scrape_all()
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(len(scrape_called) > 0)
```


## Complete Example

```python
# Workflow
'Test that HTML scraping proceeds normally when llms.txt is skipped.'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'skip_llms_txt': True}
original_cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        os.chdir(tmpdir)
        converter = DocToSkillConverter(config, dry_run=False)
        scrape_called = []

        def mock_scrape(url):
            scrape_called.append(url)
            return None
        with patch.object(converter, 'scrape_page', side_effect=mock_scrape), patch.object(converter, 'save_summary'):
            converter.scrape_all()
            self.assertTrue(len(scrape_called) > 0)
    finally:
        os.chdir(original_cwd)
```

## Next Steps


---

*Source: test_skip_llms_txt.py:295 | Complexity: Advanced | Last updated: 2026-02-14*