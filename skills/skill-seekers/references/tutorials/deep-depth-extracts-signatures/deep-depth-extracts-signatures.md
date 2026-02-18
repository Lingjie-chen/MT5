# How To: Deep Depth Extracts Signatures

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that deep depth extracts full signatures.

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.code_analyzer`


## Step-by-Step Guide

### Step 1: 'Test that deep depth extracts full signatures.'

```python
'Test that deep depth extracts full signatures.'
```

### Step 2: Assign analyzer = CodeAnalyzer(...)

```python
analyzer = CodeAnalyzer(depth='deep')
```

### Step 3: Assign code = '\ndef calculate(x: int, y: int) -> int:\n    """Calculate sum."""\n    return x + y\n'

```python
code = '\ndef calculate(x: int, y: int) -> int:\n    """Calculate sum."""\n    return x + y\n'
```

### Step 4: Assign result = analyzer.analyze_file(...)

```python
result = analyzer.analyze_file('test.py', code, 'Python')
```

### Step 5: Call self.assertIn()

```python
self.assertIn('functions', result)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(len(result['functions']), 1)
```

### Step 7: Assign func = value

```python
func = result['functions'][0]
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(func['name'], 'calculate')
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(func['return_type'], 'int')
```


## Complete Example

```python
# Workflow
'Test that deep depth extracts full signatures.'
analyzer = CodeAnalyzer(depth='deep')
code = '\ndef calculate(x: int, y: int) -> int:\n    """Calculate sum."""\n    return x + y\n'
result = analyzer.analyze_file('test.py', code, 'Python')
self.assertIn('functions', result)
self.assertEqual(len(result['functions']), 1)
func = result['functions'][0]
self.assertEqual(func['name'], 'calculate')
self.assertEqual(func['return_type'], 'int')
```

## Next Steps


---

*Source: test_code_analyzer.py:459 | Complexity: Advanced | Last updated: 2026-02-14*