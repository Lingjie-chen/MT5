# How To: Comprehensive Preset Implies Full Depth

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that --comprehensive preset should trigger full depth.

## Prerequisites

**Required Modules:**
- `sys`
- `unittest`
- `pathlib`
- `skill_seekers.cli.main`


## Step-by-Step Guide

### Step 1: 'Test that --comprehensive preset should trigger full depth.'

```python
'Test that --comprehensive preset should trigger full depth.'
```

### Step 2: Assign args = self.parser.parse_args(...)

```python
args = self.parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
```

### Step 3: Call self.assertTrue()

```python
self.assertTrue(args.comprehensive)
```


## Complete Example

```python
# Workflow
'Test that --comprehensive preset should trigger full depth.'
args = self.parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
self.assertTrue(args.comprehensive)
```

## Next Steps


---

*Source: test_analyze_command.py:170 | Complexity: Beginner | Last updated: 2026-02-14*