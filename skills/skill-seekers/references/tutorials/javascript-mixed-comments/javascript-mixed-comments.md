# How To: Javascript Mixed Comments

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test JavaScript mixed inline and block comments.

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

### Step 1: 'Test JavaScript mixed inline and block comments.'

```python
'Test JavaScript mixed inline and block comments.'
```

### Step 2: Assign code = '\n// Inline comment\n/* Block comment */\nfunction test() {\n    // Another inline\n    /* Another block */\n    return true;\n}\n'

```python
code = '\n// Inline comment\n/* Block comment */\nfunction test() {\n    // Another inline\n    /* Another block */\n    return true;\n}\n'
```

### Step 3: Assign result = self.analyzer.analyze_file(...)

```python
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
```

### Step 4: Assign comments = value

```python
comments = result['comments']
```

### Step 5: Assign inline_comments = value

```python
inline_comments = [c for c in comments if c['type'] == 'inline']
```

### Step 6: Assign block_comments = value

```python
block_comments = [c for c in comments if c['type'] == 'block']
```

### Step 7: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(inline_comments), 2)
```

### Step 8: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(block_comments), 2)
```


## Complete Example

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

# Workflow
'Test JavaScript mixed inline and block comments.'
code = '\n// Inline comment\n/* Block comment */\nfunction test() {\n    // Another inline\n    /* Another block */\n    return true;\n}\n'
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
comments = result['comments']
inline_comments = [c for c in comments if c['type'] == 'inline']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(inline_comments), 2)
self.assertGreaterEqual(len(block_comments), 2)
```

## Next Steps


---

*Source: test_code_analyzer.py:675 | Complexity: Advanced | Last updated: 2026-02-14*