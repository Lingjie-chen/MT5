# How To: Analyze Output Structure

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that output has expected structure.

## Prerequisites

**Required Modules:**
- `json`
- `shutil`
- `subprocess`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`


## Step-by-Step Guide

### Step 1: 'Test that output has expected structure.'

```python
'Test that output has expected structure.'
```

### Step 2: Assign output_dir = value

```python
output_dir = self.test_dir / 'output_structure'
```

### Step 3: Assign result = self.run_command(...)

```python
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')
```

### Step 6: Assign analysis_file = value

```python
analysis_file = output_dir / 'code_analysis.json'
```

### Step 7: Assign data = json.load(...)

```python
data = json.load(f)
```

### Step 8: Call self.assertIsInstance()

```python
self.assertIsInstance(data, (dict, list), 'code_analysis.json is not valid JSON')
```


## Complete Example

```python
# Workflow
'Test that output has expected structure.'
output_dir = self.test_dir / 'output_structure'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')
analysis_file = output_dir / 'code_analysis.json'
if analysis_file.exists():
    with open(analysis_file) as f:
        data = json.load(f)
        self.assertIsInstance(data, (dict, list), 'code_analysis.json is not valid JSON')
```

## Next Steps


---

*Source: test_analyze_e2e.py:228 | Complexity: Advanced | Last updated: 2026-02-14*