# How To: Confidence Scoring

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test confidence scores are calculated correctly

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
self.analyzer = PythonTestAnalyzer()
```

## Step-by-Step Guide

### Step 1: 'Test confidence scores are calculated correctly'

```python
'Test confidence scores are calculated correctly'
```

### Step 2: Assign simple_code = '\ndef test_simple():\n    obj = MyClass()\n    assert obj is not None\n'

```python
simple_code = '\ndef test_simple():\n    obj = MyClass()\n    assert obj is not None\n'
```

### Step 3: Assign simple_examples = self.analyzer.extract(...)

```python
simple_examples = self.analyzer.extract('test_simple.py', simple_code)
```

### Step 4: Assign complex_code = '\ndef test_complex():\n    """Test complex initialization"""\n    obj = MyClass(\n        param1="value1",\n        param2="value2",\n        param3={"nested": "dict"},\n        param4=[1, 2, 3]\n    )\n    result = obj.process()\n    assert result.status == "success"\n'

```python
complex_code = '\ndef test_complex():\n    """Test complex initialization"""\n    obj = MyClass(\n        param1="value1",\n        param2="value2",\n        param3={"nested": "dict"},\n        param4=[1, 2, 3]\n    )\n    result = obj.process()\n    assert result.status == "success"\n'
```

### Step 5: Assign complex_examples = self.analyzer.extract(...)

```python
complex_examples = self.analyzer.extract('test_complex.py', complex_code)
```

### Step 6: Assign simple_complexity = max(...)

```python
simple_complexity = max((ex.complexity_score for ex in simple_examples))
```

### Step 7: Assign complex_complexity = max(...)

```python
complex_complexity = max((ex.complexity_score for ex in complex_examples))
```

### Step 8: Call self.assertGreater()

```python
self.assertGreater(complex_complexity, simple_complexity)
```


## Complete Example

```python
# Setup
self.analyzer = PythonTestAnalyzer()

# Workflow
'Test confidence scores are calculated correctly'
simple_code = '\ndef test_simple():\n    obj = MyClass()\n    assert obj is not None\n'
simple_examples = self.analyzer.extract('test_simple.py', simple_code)
complex_code = '\ndef test_complex():\n    """Test complex initialization"""\n    obj = MyClass(\n        param1="value1",\n        param2="value2",\n        param3={"nested": "dict"},\n        param4=[1, 2, 3]\n    )\n    result = obj.process()\n    assert result.status == "success"\n'
complex_examples = self.analyzer.extract('test_complex.py', complex_code)
if simple_examples and complex_examples:
    simple_complexity = max((ex.complexity_score for ex in simple_examples))
    complex_complexity = max((ex.complexity_score for ex in complex_examples))
    self.assertGreater(complex_complexity, simple_complexity)
```

## Next Steps


---

*Source: test_test_example_extractor.py:209 | Complexity: Advanced | Last updated: 2026-02-14*