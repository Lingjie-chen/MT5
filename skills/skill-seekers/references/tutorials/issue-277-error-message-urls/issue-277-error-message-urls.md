# How To: Issue 277 Error Message Urls

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test the exact URLs that appeared in error messages from the issue report.
These were the actual 404-causing URLs that need to be fixed.

## Prerequisites

**Required Modules:**
- `unittest`
- `unittest.mock`
- `skill_seekers.cli.doc_scraper`


## Step-by-Step Guide

### Step 1: '\n        Test the exact URLs that appeared in error messages from the issue report.\n        These were the actual 404-causing URLs that need to be fixed.\n        '

```python
'\n        Test the exact URLs that appeared in error messages from the issue report.\n        These were the actual 404-causing URLs that need to be fixed.\n        '
```

### Step 2: Assign error_urls_with_anchors = value

```python
error_urls_with_anchors = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization/index.html.md', 'https://mikro-orm.io/docs/defining-entities#formulas/index.html.md', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums/index.html.md']
```

### Step 3: Assign input_urls = value

```python
input_urls = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization', 'https://mikro-orm.io/docs/propagation', 'https://mikro-orm.io/docs/defining-entities#formulas', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums']
```

### Step 4: Assign result = self.converter._convert_to_md_urls(...)

```python
result = self.converter._convert_to_md_urls(input_urls)
```

### Step 5: Assign correct_urls = value

```python
correct_urls = ['https://mikro-orm.io/docs/quick-start/index.html.md', 'https://mikro-orm.io/docs/propagation/index.html.md', 'https://mikro-orm.io/docs/defining-entities/index.html.md']
```

### Step 6: Call self.assertNotIn()

```python
self.assertNotIn(error_url, result, f'Should not generate the 404-causing URL: {error_url}')
```

### Step 7: Call self.assertIn()

```python
self.assertIn(correct_url, result, f'Should generate the correct URL: {correct_url}')
```


## Complete Example

```python
# Workflow
'\n        Test the exact URLs that appeared in error messages from the issue report.\n        These were the actual 404-causing URLs that need to be fixed.\n        '
error_urls_with_anchors = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization/index.html.md', 'https://mikro-orm.io/docs/defining-entities#formulas/index.html.md', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums/index.html.md']
input_urls = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization', 'https://mikro-orm.io/docs/propagation', 'https://mikro-orm.io/docs/defining-entities#formulas', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums']
result = self.converter._convert_to_md_urls(input_urls)
for error_url in error_urls_with_anchors:
    self.assertNotIn(error_url, result, f'Should not generate the 404-causing URL: {error_url}')
correct_urls = ['https://mikro-orm.io/docs/quick-start/index.html.md', 'https://mikro-orm.io/docs/propagation/index.html.md', 'https://mikro-orm.io/docs/defining-entities/index.html.md']
for correct_url in correct_urls:
    self.assertIn(correct_url, result, f'Should generate the correct URL: {correct_url}')
```

## Next Steps


---

*Source: test_issue_277_real_world.py:213 | Complexity: Intermediate | Last updated: 2026-02-14*