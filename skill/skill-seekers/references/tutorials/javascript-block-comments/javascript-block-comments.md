# How To: Javascript Block Comments

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test JavaScript /* */ block comment extraction.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.code_analyzer`

**Setup Required:**
```python
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')
```

## Step-by-Step Guide

### Step 1: 'Test JavaScript /* */ block comment extraction.'

```python
'Test JavaScript /* */ block comment extraction.'
```

### Step 2: Assign code = '\n/* This is a\n   multi-line\n   block comment */\nfunction test() {\n    /* Another block comment */\n    return 42;\n}\n'

```python
code = '\n/* This is a\n   multi-line\n   block comment */\nfunction test() {\n    /* Another block comment */\n    return 42;\n}\n'
```

### Step 3: Assign result = self.analyzer.analyze_file(...)

```python
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
```

### Step 4: Assign comments = value

```python
comments = result['comments']
```

### Step 5: Assign block_comments = value

```python
block_comments = [c for c in comments if c['type'] == 'block']
```

### Step 6: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(block_comments), 2)
```

### Step 7: Assign first_block = next(...)

```python
first_block = next((c for c in comments if 'multi-line' in c['text']))
```

### Step 8: Call self.assertIn()

```python
self.assertIn('multi-line', first_block['text'])
```


## Complete Example

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

# Workflow
'Test JavaScript /* */ block comment extraction.'
code = '\n/* This is a\n   multi-line\n   block comment */\nfunction test() {\n    /* Another block comment */\n    return 42;\n}\n'
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
comments = result['comments']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(block_comments), 2)
first_block = next((c for c in comments if 'multi-line' in c['text']))
self.assertIn('multi-line', first_block['text'])
```

## Next Steps


---

*Source: test_code_analyzer.py:652 | Complexity: Advanced | Last updated: 2026-02-14*