# How To: Cpp Comment Extraction

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test C++ comment extraction (uses same logic as JavaScript).

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

### Step 1: 'Test C++ comment extraction (uses same logic as JavaScript).'

```python
'Test C++ comment extraction (uses same logic as JavaScript).'
```

### Step 2: Assign code = '\n// Header comment\nclass Node {\npublic:\n    // Method comment\n    void update();\n\n    /* Block comment for data member */\n    int value;\n};\n'

```python
code = '\n// Header comment\nclass Node {\npublic:\n    // Method comment\n    void update();\n\n    /* Block comment for data member */\n    int value;\n};\n'
```

### Step 3: Assign result = self.analyzer.analyze_file(...)

```python
result = self.analyzer.analyze_file('test.h', code, 'C++')
```

### Step 4: Call self.assertIn()

```python
self.assertIn('comments', result)
```

### Step 5: Assign comments = value

```python
comments = result['comments']
```

### Step 6: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(comments), 3)
```

### Step 7: Assign inline_comments = value

```python
inline_comments = [c for c in comments if c['type'] == 'inline']
```

### Step 8: Assign block_comments = value

```python
block_comments = [c for c in comments if c['type'] == 'block']
```

### Step 9: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(inline_comments), 2)
```

### Step 10: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(len(block_comments), 1)
```


## Complete Example

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

# Workflow
'Test C++ comment extraction (uses same logic as JavaScript).'
code = '\n// Header comment\nclass Node {\npublic:\n    // Method comment\n    void update();\n\n    /* Block comment for data member */\n    int value;\n};\n'
result = self.analyzer.analyze_file('test.h', code, 'C++')
self.assertIn('comments', result)
comments = result['comments']
self.assertGreaterEqual(len(comments), 3)
inline_comments = [c for c in comments if c['type'] == 'inline']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(inline_comments), 2)
self.assertGreaterEqual(len(block_comments), 1)
```

## Next Steps


---

*Source: test_code_analyzer.py:697 | Complexity: Advanced | Last updated: 2026-02-14*