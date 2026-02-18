# How To: Parameter Table Generation

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test parameter table formatting.

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

### Step 1: 'Test parameter table formatting.'

```python
'Test parameter table formatting.'
```

### Step 2: Assign code_analysis = value

```python
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'create_user', 'parameters': [{'name': 'name', 'type_hint': 'str', 'default': None}, {'name': 'age', 'type_hint': 'int', 'default': '18'}, {'name': 'active', 'type_hint': 'bool', 'default': 'True'}], 'return_type': 'dict', 'docstring': 'Create a user object.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
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
self.assertIn('**Parameters**:', content)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('| Name | Type | Default | Description |', content)
```

### Step 9: Call self.assertIn()

```python
self.assertIn('| name | str | - |', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('| age | int | 18 |', content)
```

### Step 11: Call self.assertIn()

```python
self.assertIn('| active | bool | True |', content)
```


## Complete Example

```python
# Workflow
'Test parameter table formatting.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'create_user', 'parameters': [{'name': 'name', 'type_hint': 'str', 'default': None}, {'name': 'age', 'type_hint': 'int', 'default': '18'}, {'name': 'active', 'type_hint': 'bool', 'default': 'True'}], 'return_type': 'dict', 'docstring': 'Create a user object.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('**Parameters**:', content)
self.assertIn('| Name | Type | Default | Description |', content)
self.assertIn('| name | str | - |', content)
self.assertIn('| age | int | 18 |', content)
self.assertIn('| active | bool | True |', content)
```

## Next Steps


---

*Source: test_api_reference_builder.py:124 | Complexity: Advanced | Last updated: 2026-02-14*