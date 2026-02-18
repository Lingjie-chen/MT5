# How To: Valid Complete Config

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test valid complete configuration

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.doc_scraper`


## Step-by-Step Guide

### Step 1: 'Test valid complete configuration'

```python
'Test valid complete configuration'
```

### Step 2: Assign config = value

```python
config = {'name': 'godot', 'base_url': 'https://docs.godotengine.org/en/stable/', 'description': 'Godot Engine documentation', 'selectors': {'main_content': 'div[role="main"]', 'title': 'title', 'code_blocks': 'pre code'}, 'url_patterns': {'include': ['/guide/', '/api/'], 'exclude': ['/blog/']}, 'categories': {'getting_started': ['intro', 'tutorial'], 'api': ['api', 'reference']}, 'rate_limit': 0.5, 'max_pages': 500}
```

### Step 3: Assign unknown = validate_config(...)

```python
errors, _ = validate_config(config)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')
```


## Complete Example

```python
# Workflow
'Test valid complete configuration'
config = {'name': 'godot', 'base_url': 'https://docs.godotengine.org/en/stable/', 'description': 'Godot Engine documentation', 'selectors': {'main_content': 'div[role="main"]', 'title': 'title', 'code_blocks': 'pre code'}, 'url_patterns': {'include': ['/guide/', '/api/'], 'exclude': ['/blog/']}, 'categories': {'getting_started': ['intro', 'tutorial'], 'api': ['api', 'reference']}, 'rate_limit': 0.5, 'max_pages': 500}
errors, _ = validate_config(config)
self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')
```

## Next Steps


---

*Source: test_config_validation.py:27 | Complexity: Intermediate | Last updated: 2026-02-14*