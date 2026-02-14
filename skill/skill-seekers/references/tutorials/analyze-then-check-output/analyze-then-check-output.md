# How To: Analyze Then Check Output

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test analyzing and verifying output can be read.

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

### Step 1: 'Test analyzing and verifying output can be read.'

```python
'Test analyzing and verifying output can be read.'
```

### Step 2: Assign output_dir = value

```python
output_dir = self.test_dir / 'output'
```

### Step 3: Assign result = subprocess.run(...)

```python
result = subprocess.run(['skill-seekers', 'analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick'], capture_output=True, text=True, timeout=120)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
```

### Step 5: Assign skill_file = value

```python
skill_file = output_dir / 'SKILL.md'
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(skill_file.exists(), 'SKILL.md not created')
```

### Step 7: Assign content = skill_file.read_text(...)

```python
content = skill_file.read_text()
```

### Step 8: Call self.assertGreater()

```python
self.assertGreater(len(content), 50, 'Output too short')
```

### Step 9: Call self.assertIn()

```python
self.assertIn('Codebase', content, 'Missing codebase header')
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')
```


## Complete Example

```python
# Workflow
'Test analyzing and verifying output can be read.'
output_dir = self.test_dir / 'output'
result = subprocess.run(['skill-seekers', 'analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick'], capture_output=True, text=True, timeout=120)
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not created')
content = skill_file.read_text()
self.assertGreater(len(content), 50, 'Output too short')
self.assertIn('Codebase', content, 'Missing codebase header')
self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')
```

## Next Steps


---

*Source: test_analyze_e2e.py:283 | Complexity: Advanced | Last updated: 2026-02-14*