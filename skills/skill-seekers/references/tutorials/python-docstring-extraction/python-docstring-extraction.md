# How To: Python Docstring Extraction

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test docstring extraction for functions and classes.

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.code_analyzer`


## Step-by-Step Guide

### Step 1: 'Test docstring extraction for functions and classes.'

```python
'Test docstring extraction for functions and classes.'
```

### Step 2: Assign code = '\nclass Calculator:\n    """A simple calculator class.\n\n    Supports basic arithmetic operations.\n    """\n\n    def add(self, a, b):\n        """Add two numbers.\n\n        Args:\n            a: First number\n            b: Second number\n\n        Returns:\n            Sum of a and b\n        """\n        return a + b\n'

```python
code = '\nclass Calculator:\n    """A simple calculator class.\n\n    Supports basic arithmetic operations.\n    """\n\n    def add(self, a, b):\n        """Add two numbers.\n\n        Args:\n            a: First number\n            b: Second number\n\n        Returns:\n            Sum of a and b\n        """\n        return a + b\n'
```

### Step 3: Assign result = self.analyzer.analyze_file(...)

```python
result = self.analyzer.analyze_file('test.py', code, 'Python')
```

### Step 4: Assign calc_class = value

```python
calc_class = result['classes'][0]
```

### Step 5: Call self.assertIn()

```python
self.assertIn('A simple calculator class', calc_class['docstring'])
```

### Step 6: Call self.assertIn()

```python
self.assertIn('Supports basic arithmetic operations', calc_class['docstring'])
```

### Step 7: Assign add_method = value

```python
add_method = calc_class['methods'][0]
```

### Step 8: Call self.assertIn()

```python
self.assertIn('Add two numbers', add_method['docstring'])
```

### Step 9: Call self.assertIn()

```python
self.assertIn('Args:', add_method['docstring'])
```

### Step 10: Call self.assertIn()

```python
self.assertIn('Returns:', add_method['docstring'])
```


## Complete Example

```python
# Workflow
'Test docstring extraction for functions and classes.'
code = '\nclass Calculator:\n    """A simple calculator class.\n\n    Supports basic arithmetic operations.\n    """\n\n    def add(self, a, b):\n        """Add two numbers.\n\n        Args:\n            a: First number\n            b: Second number\n\n        Returns:\n            Sum of a and b\n        """\n        return a + b\n'
result = self.analyzer.analyze_file('test.py', code, 'Python')
calc_class = result['classes'][0]
self.assertIn('A simple calculator class', calc_class['docstring'])
self.assertIn('Supports basic arithmetic operations', calc_class['docstring'])
add_method = calc_class['methods'][0]
self.assertIn('Add two numbers', add_method['docstring'])
self.assertIn('Args:', add_method['docstring'])
self.assertIn('Returns:', add_method['docstring'])
```

## Next Steps


---

*Source: test_code_analyzer.py:134 | Complexity: Advanced | Last updated: 2026-02-14*