# How To: Async Function Indicator

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that async functions are marked in output.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.api_reference_builder`

**Required Fixtures:**
- `api_client` fixture

**Setup Required:**
```python
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'
```

## Step-by-Step Guide

### Step 1: 'Test that async functions are marked in output.'

```python
'Test that async functions are marked in output.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'async_utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'fetch_data', 'parameters': [{'name': 'url', 'type_hint': 'str', 'default': None}], 'return_type': 'dict', 'docstring': 'Fetch data from URL.', 'is_async': True, 'is_method': False, 'decorators': []}]}]}
```

### Step 3: Assign builder = APIReferenceBuilder(...)

```python
builder = APIReferenceBuilder(code_analysis)
```

### Step 4: Assign generated = builder.build_reference(...)

```python
generated = builder.build_reference(self.output_dir)
```

### Step 5: Assign output_file = value

```python
output_file = list(generated.values())[0]
```

### Step 6: Assign content = output_file.read_text(...)

```python
content = output_file.read_text()
```

### Step 7: Call self.assertIn()

```python
self.assertIn('**Async function**', content)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('fetch_data', content)
```


## Complete Example

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

# Workflow
'Test that async functions are marked in output.'
code_analysis = {'files': [{'file': 'async_utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'fetch_data', 'parameters': [{'name': 'url', 'type_hint': 'str', 'default': None}], 'return_type': 'dict', 'docstring': 'Fetch data from URL.', 'is_async': True, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('**Async function**', content)
self.assertIn('fetch_data', content)
```

## Next Steps


---

*Source: test_api_reference_builder.py:288 | Complexity: Advanced | Last updated: 2026-02-14*