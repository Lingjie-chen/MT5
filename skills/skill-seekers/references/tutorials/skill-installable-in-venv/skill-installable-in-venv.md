# How To: Skill Installable In Venv

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Test skill is installable in clean virtual environment

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `subprocess`
- `sys`
- `pathlib`
- `pytest`
- `skill_seekers.cli.adaptors`

**Setup Required:**
```python
# Fixtures: run_bootstrap, output_skill_dir, tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test skill is installable in clean virtual environment'

```python
'Test skill is installable in clean virtual environment'
```

**Verification:**
```python
assert result.returncode == 0
```

### Step 2: Assign result = run_bootstrap(...)

```python
result = run_bootstrap()
```

**Verification:**
```python
assert result.returncode == 0, f'Install failed: {result.stderr}'
```

### Step 3: Assign venv_path = value

```python
venv_path = tmp_path / 'test_venv'
```

### Step 4: Call subprocess.run()

```python
subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True, timeout=60)
```

### Step 5: Assign pip_path = value

```python
pip_path = venv_path / 'bin' / 'pip'
```

### Step 6: Assign result = subprocess.run(...)

```python
result = subprocess.run([str(pip_path), 'install', '-e', '.'], cwd=output_skill_dir.parent.parent, capture_output=True, text=True, timeout=120)
```

**Verification:**
```python
assert result.returncode == 0, f'Install failed: {result.stderr}'
```


## Complete Example

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir, tmp_path

# Workflow
'Test skill is installable in clean virtual environment'
result = run_bootstrap()
assert result.returncode == 0
venv_path = tmp_path / 'test_venv'
subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True, timeout=60)
pip_path = venv_path / 'bin' / 'pip'
result = subprocess.run([str(pip_path), 'install', '-e', '.'], cwd=output_skill_dir.parent.parent, capture_output=True, text=True, timeout=120)
assert result.returncode == 0, f'Install failed: {result.stderr}'
```

## Next Steps


---

*Source: test_bootstrap_skill_e2e.py:122 | Complexity: Intermediate | Last updated: 2026-02-14*