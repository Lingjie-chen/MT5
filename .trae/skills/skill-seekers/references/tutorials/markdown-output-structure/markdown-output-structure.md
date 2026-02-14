# How To: Markdown Output Structure

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test overall markdown document structure.

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

### Step 1: 'Test overall markdown document structure.'

```python
'Test overall markdown document structure.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'module.py', 'language': 'Python', 'classes': [{'name': 'TestClass', 'docstring': 'Test class.', 'base_classes': [], 'methods': []}], 'functions': [{'name': 'test_func', 'parameters': [], 'return_type': None, 'docstring': 'Test function.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
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
self.assertIn('# API Reference: module.py', content)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('**Language**: Python', content)
```

### Step 9: Call self.assertIn()

```python
self.assertIn('**Source**: `module.py`', content)
```

### Step 10: Assign classes_pos = content.find(...)

```python
classes_pos = content.find('## Classes')
```

### Step 11: Assign functions_pos = content.find(...)

```python
functions_pos = content.find('## Functions')
```

### Step 12: Call self.assertNotEqual()

```python
self.assertNotEqual(classes_pos, -1)
```

### Step 13: Call self.assertNotEqual()

```python
self.assertNotEqual(functions_pos, -1)
```

### Step 14: Call self.assertLess()

```python
self.assertLess(classes_pos, functions_pos)
```


## Complete Example

```python
# Workflow
'Test overall markdown document structure.'
code_analysis = {'files': [{'file': 'module.py', 'language': 'Python', 'classes': [{'name': 'TestClass', 'docstring': 'Test class.', 'base_classes': [], 'methods': []}], 'functions': [{'name': 'test_func', 'parameters': [], 'return_type': None, 'docstring': 'Test function.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('# API Reference: module.py', content)
self.assertIn('**Language**: Python', content)
self.assertIn('**Source**: `module.py`', content)
classes_pos = content.find('## Classes')
functions_pos = content.find('## Functions')
self.assertNotEqual(classes_pos, -1)
self.assertNotEqual(functions_pos, -1)
self.assertLess(classes_pos, functions_pos)
```

## Next Steps


---

*Source: test_api_reference_builder.py:164 | Complexity: Advanced | Last updated: 2026-02-14*