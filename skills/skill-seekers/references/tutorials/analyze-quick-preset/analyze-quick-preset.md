# How To: Analyze Quick Preset

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test quick analysis preset (real execution).

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

### Step 1: 'Test quick analysis preset (real execution).'

```python
'Test quick analysis preset (real execution).'
```

### Step 2: Assign output_dir = value

```python
output_dir = self.test_dir / 'output_quick'
```

### Step 3: Assign result = self.run_command(...)

```python
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(result.returncode, 0, f'Quick analysis failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(output_dir.exists(), 'Output directory not created')
```

### Step 6: Assign skill_file = value

```python
skill_file = output_dir / 'SKILL.md'
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(skill_file.exists(), 'SKILL.md not generated')
```

### Step 8: Assign skill_content = skill_file.read_text(...)

```python
skill_content = skill_file.read_text()
```

### Step 9: Call self.assertGreater()

```python
self.assertGreater(len(skill_content), 100, 'SKILL.md is too short')
```

### Step 10: Call self.assertIn()

```python
self.assertIn('Codebase', skill_content, 'Missing codebase header')
```

### Step 11: Call self.assertIn()

```python
self.assertIn('Analysis', skill_content, 'Missing analysis section')
```

### Step 12: Call self.assertTrue()

```python
self.assertTrue(skill_content.startswith('---'), 'Missing YAML frontmatter')
```

### Step 13: Call self.assertIn()

```python
self.assertIn('name:', skill_content, 'Missing name in frontmatter')
```


## Complete Example

```python
# Workflow
'Test quick analysis preset (real execution).'
output_dir = self.test_dir / 'output_quick'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Quick analysis failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
self.assertTrue(output_dir.exists(), 'Output directory not created')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not generated')
skill_content = skill_file.read_text()
self.assertGreater(len(skill_content), 100, 'SKILL.md is too short')
self.assertIn('Codebase', skill_content, 'Missing codebase header')
self.assertIn('Analysis', skill_content, 'Missing analysis section')
self.assertTrue(skill_content.startswith('---'), 'Missing YAML frontmatter')
self.assertIn('name:', skill_content, 'Missing name in frontmatter')
```

## Next Steps


---

*Source: test_analyze_e2e.py:106 | Complexity: Advanced | Last updated: 2026-02-14*