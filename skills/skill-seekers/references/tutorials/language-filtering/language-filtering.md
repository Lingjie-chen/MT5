# How To: Language Filtering

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test filtering by programming language

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.test_example_extractor`

**Setup Required:**
```python
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)
```

## Step-by-Step Guide

### Step 1: 'Test filtering by programming language'

```python
'Test filtering by programming language'
```

### Step 2: Assign py_file = value

```python
py_file = self.temp_dir / 'test_py.py'
```

### Step 3: Call py_file.write_text()

```python
py_file.write_text('\ndef test_python():\n    obj = MyClass(param="value")\n    assert obj is not None\n')
```

### Step 4: Assign js_file = value

```python
js_file = self.temp_dir / 'test_js.js'
```

### Step 5: Call js_file.write_text()

```python
js_file.write_text('\ntest("javascript test", () => {\n    const obj = new MyClass();\n    expect(obj).toBeDefined();\n});\n')
```

### Step 6: Assign python_extractor = TestExampleExtractor(...)

```python
python_extractor = TestExampleExtractor(languages=['python'])
```

### Step 7: Assign report = python_extractor.extract_from_directory(...)

```python
report = python_extractor.extract_from_directory(self.temp_dir)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(example.language, 'Python')
```


## Complete Example

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

# Workflow
'Test filtering by programming language'
py_file = self.temp_dir / 'test_py.py'
py_file.write_text('\ndef test_python():\n    obj = MyClass(param="value")\n    assert obj is not None\n')
js_file = self.temp_dir / 'test_js.js'
js_file.write_text('\ntest("javascript test", () => {\n    const obj = new MyClass();\n    expect(obj).toBeDefined();\n});\n')
python_extractor = TestExampleExtractor(languages=['python'])
report = python_extractor.extract_from_directory(self.temp_dir)
for example in report.examples:
    self.assertEqual(example.language, 'Python')
```

## Next Steps


---

*Source: test_test_example_extractor.py:622 | Complexity: Advanced | Last updated: 2026-02-14*