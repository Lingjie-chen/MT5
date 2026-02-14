# How To: Valid Name Formats

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test various valid name formats

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.doc_scraper`


## Step-by-Step Guide

### Step 1: 'Test various valid name formats'

```python
'Test various valid name formats'
```

### Step 2: Assign valid_names = value

```python
valid_names = ['test', 'test-skill', 'test_skill', 'TestSkill123', 'my-awesome-skill_v2']
```

### Step 3: Assign config = value

```python
config = {'name': name, 'base_url': 'https://example.com/'}
```

### Step 4: Assign unknown = validate_config(...)

```python
errors, _ = validate_config(config)
```

### Step 5: Assign name_errors = value

```python
name_errors = [e for e in errors if 'invalid name' in e.lower()]
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(len(name_errors), 0, f"Name '{name}' should be valid")
```


## Complete Example

```python
# Workflow
'Test various valid name formats'
valid_names = ['test', 'test-skill', 'test_skill', 'TestSkill123', 'my-awesome-skill_v2']
for name in valid_names:
    config = {'name': name, 'base_url': 'https://example.com/'}
    errors, _ = validate_config(config)
    name_errors = [e for e in errors if 'invalid name' in e.lower()]
    self.assertEqual(len(name_errors), 0, f"Name '{name}' should be valid")
```

## Next Steps


---

*Source: test_config_validation.py:64 | Complexity: Intermediate | Last updated: 2026-02-14*