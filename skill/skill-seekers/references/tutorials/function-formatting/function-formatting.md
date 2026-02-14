# How To: Function Formatting

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test markdown formatting for function signatures.

## Prerequisites

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.api_reference_builder`


## Step-by-Step Guide

### Step 1: 'Test markdown formatting for function signatures.'

```python
'Test markdown formatting for function signatures.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'calculate_sum', 'parameters': [{'name': 'numbers', 'type_hint': 'list', 'default': None}], 'return_type': 'int', 'docstring': 'Calculate sum of numbers.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
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
self.assertIn('## Functions', content)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('### calculate_sum', content)
```

### Step 9: Call self.assertIn()

```python
self.assertIn('Calculate sum of numbers', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('**Returns**: `int`', content)
```


## Complete Example

```python
# Workflow
'Test markdown formatting for function signatures.'
code_analysis = {'files': [{'file': 'utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'calculate_sum', 'parameters': [{'name': 'numbers', 'type_hint': 'list', 'default': None}], 'return_type': 'int', 'docstring': 'Calculate sum of numbers.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('## Functions', content)
self.assertIn('### calculate_sum', content)
self.assertIn('Calculate sum of numbers', content)
self.assertIn('**Returns**: `int`', content)
```

## Next Steps


---

*Source: test_api_reference_builder.py:87 | Complexity: Advanced | Last updated: 2026-02-14*