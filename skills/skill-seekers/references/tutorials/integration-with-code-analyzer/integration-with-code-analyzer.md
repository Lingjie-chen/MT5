# How To: Integration With Code Analyzer

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test integration with actual code analyzer output format.

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

### Step 1: 'Test integration with actual code analyzer output format.'

```python
'Test integration with actual code analyzer output format.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'calculator.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'base_classes': [], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'float', 'default': None}, {'name': 'b', 'type_hint': 'float', 'default': None}], 'return_type': 'float', 'docstring': 'Add two numbers.', 'decorators': [], 'is_async': False, 'is_method': True}], 'docstring': 'Calculator class.', 'line_number': 1}], 'functions': []}, {'file': 'utils.js', 'language': 'JavaScript', 'classes': [], 'functions': [{'name': 'formatDate', 'parameters': [{'name': 'date', 'type_hint': None, 'default': None}], 'return_type': None, 'docstring': None, 'is_async': False, 'is_method': False, 'decorators': []}]}]}
```

### Step 3: Assign builder = APIReferenceBuilder(...)

```python
builder = APIReferenceBuilder(code_analysis)
```

### Step 4: Assign generated = builder.build_reference(...)

```python
generated = builder.build_reference(self.output_dir)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(generated), 2)
```

### Step 6: Assign filenames = value

```python
filenames = [f.name for f in generated.values()]
```

### Step 7: Call self.assertIn()

```python
self.assertIn('calculator.md', filenames)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('utils.md', filenames)
```

### Step 9: Assign py_file = next(...)

```python
py_file = next((f for f in generated.values() if f.name == 'calculator.md'))
```

### Step 10: Assign py_content = py_file.read_text(...)

```python
py_content = py_file.read_text()
```

### Step 11: Call self.assertIn()

```python
self.assertIn('Calculator class', py_content)
```

### Step 12: Call self.assertIn()

```python
self.assertIn('add(a: float, b: float) → float', py_content)
```

### Step 13: Assign js_file = next(...)

```python
js_file = next((f for f in generated.values() if f.name == 'utils.md'))
```

### Step 14: Assign js_content = js_file.read_text(...)

```python
js_content = js_file.read_text()
```

### Step 15: Call self.assertIn()

```python
self.assertIn('formatDate', js_content)
```

### Step 16: Call self.assertIn()

```python
self.assertIn('**Language**: JavaScript', js_content)
```


## Complete Example

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

# Workflow
'Test integration with actual code analyzer output format.'
code_analysis = {'files': [{'file': 'calculator.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'base_classes': [], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'float', 'default': None}, {'name': 'b', 'type_hint': 'float', 'default': None}], 'return_type': 'float', 'docstring': 'Add two numbers.', 'decorators': [], 'is_async': False, 'is_method': True}], 'docstring': 'Calculator class.', 'line_number': 1}], 'functions': []}, {'file': 'utils.js', 'language': 'JavaScript', 'classes': [], 'functions': [{'name': 'formatDate', 'parameters': [{'name': 'date', 'type_hint': None, 'default': None}], 'return_type': None, 'docstring': None, 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
self.assertEqual(len(generated), 2)
filenames = [f.name for f in generated.values()]
self.assertIn('calculator.md', filenames)
self.assertIn('utils.md', filenames)
py_file = next((f for f in generated.values() if f.name == 'calculator.md'))
py_content = py_file.read_text()
self.assertIn('Calculator class', py_content)
self.assertIn('add(a: float, b: float) → float', py_content)
js_file = next((f for f in generated.values() if f.name == 'utils.md'))
js_content = js_file.read_text()
self.assertIn('formatDate', js_content)
self.assertIn('**Language**: JavaScript', js_content)
```

## Next Steps


---

*Source: test_api_reference_builder.py:214 | Complexity: Advanced | Last updated: 2026-02-14*