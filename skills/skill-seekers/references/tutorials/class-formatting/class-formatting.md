# How To: Class Formatting

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test markdown formatting for class signatures.

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

### Step 1: 'Test markdown formatting for class signatures.'

```python
'Test markdown formatting for class signatures.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'docstring': 'A simple calculator class.', 'base_classes': ['object'], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'int', 'default': None}, {'name': 'b', 'type_hint': 'int', 'default': None}], 'return_type': 'int', 'docstring': 'Add two numbers.', 'is_async': False, 'is_method': True, 'decorators': []}]}], 'functions': []}]}
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
self.assertEqual(len(generated), 1)
```

### Step 6: Assign output_file = value

```python
output_file = list(generated.values())[0]
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(output_file.exists())
```

### Step 8: Assign content = output_file.read_text(...)

```python
content = output_file.read_text()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('### Calculator', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('A simple calculator class', content)
```

### Step 11: Call self.assertIn()

```python
self.assertIn('**Inherits from**: object', content)
```

### Step 12: Call self.assertIn()

```python
self.assertIn('##### add', content)
```

### Step 13: Call self.assertIn()

```python
self.assertIn('Add two numbers', content)
```


## Complete Example

```python
# Workflow
'Test markdown formatting for class signatures.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'docstring': 'A simple calculator class.', 'base_classes': ['object'], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'int', 'default': None}, {'name': 'b', 'type_hint': 'int', 'default': None}], 'return_type': 'int', 'docstring': 'Add two numbers.', 'is_async': False, 'is_method': True, 'decorators': []}]}], 'functions': []}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
self.assertEqual(len(generated), 1)
output_file = list(generated.values())[0]
self.assertTrue(output_file.exists())
content = output_file.read_text()
self.assertIn('### Calculator', content)
self.assertIn('A simple calculator class', content)
self.assertIn('**Inherits from**: object', content)
self.assertIn('##### add', content)
self.assertIn('Add two numbers', content)
```

## Next Steps


---

*Source: test_api_reference_builder.py:38 | Complexity: Advanced | Last updated: 2026-02-14*