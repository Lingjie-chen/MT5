# How To: With Configs Prefix

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test resolution with configs/ prefix.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `unittest.mock`
- `httpx`
- `pytest`
- `skill_seekers.cli.config_fetcher`
- `os`
- `os`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test resolution with configs/ prefix.'

```python
'Test resolution with configs/ prefix.'
```

**Verification:**
```python
assert result is not None
```

### Step 2: Assign configs_dir = value

```python
configs_dir = tmp_path / 'configs'
```

**Verification:**
```python
assert result.exists()
```

### Step 3: Call configs_dir.mkdir()

```python
configs_dir.mkdir()
```

**Verification:**
```python
assert result.name == 'test.json'
```

### Step 4: Assign config_file = value

```python
config_file = configs_dir / 'test.json'
```

### Step 5: Call config_file.write_text()

```python
config_file.write_text('{"name": "test"}')
```

### Step 6: Assign original_cwd = os.getcwd(...)

```python
original_cwd = os.getcwd()
```

### Step 7: Call os.chdir()

```python
os.chdir(tmp_path)
```

### Step 8: Assign result = resolve_config_path(...)

```python
result = resolve_config_path('test.json', auto_fetch=False)
```

**Verification:**
```python
assert result is not None
```

### Step 9: Call os.chdir()

```python
os.chdir(original_cwd)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test resolution with configs/ prefix.'
configs_dir = tmp_path / 'configs'
configs_dir.mkdir()
config_file = configs_dir / 'test.json'
config_file.write_text('{"name": "test"}')
import os
original_cwd = os.getcwd()
try:
    os.chdir(tmp_path)
    result = resolve_config_path('test.json', auto_fetch=False)
    assert result is not None
    assert result.exists()
    assert result.name == 'test.json'
finally:
    os.chdir(original_cwd)
```

## Next Steps


---

*Source: test_config_fetcher.py:239 | Complexity: Advanced | Last updated: 2026-02-14*