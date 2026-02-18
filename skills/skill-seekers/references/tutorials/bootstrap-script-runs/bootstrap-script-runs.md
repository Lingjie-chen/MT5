# How To: Bootstrap Script Runs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Test that bootstrap script runs successfully.

Note: This test is slow as it runs full codebase analysis.
Run with: pytest -m slow

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `subprocess`
- `pathlib`
- `pytest`

**Setup Required:**
```python
# Fixtures: project_root
```

## Step-by-Step Guide

### Step 1: 'Test that bootstrap script runs successfully.\n\n        Note: This test is slow as it runs full codebase analysis.\n        Run with: pytest -m slow\n        '

```python
'Test that bootstrap script runs successfully.\n\n        Note: This test is slow as it runs full codebase analysis.\n        Run with: pytest -m slow\n        '
```

**Verification:**
```python
assert result.returncode == 0, f'Script failed: {result.stderr}'
```

### Step 2: Assign script = value

```python
script = project_root / 'scripts' / 'bootstrap_skill.sh'
```

**Verification:**
```python
assert output_dir.exists(), 'Output directory should be created'
```

### Step 3: Assign result = subprocess.run(...)

```python
result = subprocess.run(['bash', str(script)], cwd=project_root, capture_output=True, text=True, timeout=600)
```

**Verification:**
```python
assert skill_md.exists(), 'SKILL.md should be created'
```

### Step 4: Assign output_dir = value

```python
output_dir = project_root / 'output' / 'skill-seekers'
```

**Verification:**
```python
assert '## Prerequisites' in content, 'SKILL.md should have header prepended'
```

### Step 5: Assign skill_md = value

```python
skill_md = output_dir / 'SKILL.md'
```

**Verification:**
```python
assert 'pip install skill-seekers' in content, 'SKILL.md should have install instructions'
```

### Step 6: Assign content = skill_md.read_text(...)

```python
content = skill_md.read_text()
```

**Verification:**
```python
assert '## Prerequisites' in content, 'SKILL.md should have header prepended'
```


## Complete Example

```python
# Setup
# Fixtures: project_root

# Workflow
'Test that bootstrap script runs successfully.\n\n        Note: This test is slow as it runs full codebase analysis.\n        Run with: pytest -m slow\n        '
script = project_root / 'scripts' / 'bootstrap_skill.sh'
result = subprocess.run(['bash', str(script)], cwd=project_root, capture_output=True, text=True, timeout=600)
assert result.returncode == 0, f'Script failed: {result.stderr}'
output_dir = project_root / 'output' / 'skill-seekers'
assert output_dir.exists(), 'Output directory should be created'
skill_md = output_dir / 'SKILL.md'
assert skill_md.exists(), 'SKILL.md should be created'
content = skill_md.read_text()
assert '## Prerequisites' in content, 'SKILL.md should have header prepended'
assert 'pip install skill-seekers' in content, 'SKILL.md should have install instructions'
```

## Next Steps


---

*Source: test_bootstrap_skill.py:54 | Complexity: Intermediate | Last updated: 2026-02-14*