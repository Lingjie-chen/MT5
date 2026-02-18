# How To: Config Name Normalization

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test various config name formats.

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

### Step 1: 'Test various config name formats.'

```python
'Test various config name formats.'
```

**Verification:**
```python
assert result is not None, f'Failed for {config_name}'
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
assert result.name == 'react.json'
```

### Step 4: Assign config_file = value

```python
config_file = configs_dir / 'react.json'
```

### Step 5: Call config_file.write_text()

```python
config_file.write_text('{"name": "react"}')
```

### Step 6: Assign original_cwd = os.getcwd(...)

```python
original_cwd = os.getcwd()
```

### Step 7: Call os.chdir()

```python
os.chdir(tmp_path)
```

### Step 8: Assign test_cases = value

```python
test_cases = ['react.json', 'configs/react.json']
```

### Step 9: Call os.chdir()

```python
os.chdir(original_cwd)
```

### Step 10: Assign result = resolve_config_path(...)

```python
result = resolve_config_path(config_name, auto_fetch=False)
```

**Verification:**
```python
assert result is not None, f'Failed for {config_name}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test various config name formats.'
configs_dir = tmp_path / 'configs'
configs_dir.mkdir()
config_file = configs_dir / 'react.json'
config_file.write_text('{"name": "react"}')
import os
original_cwd = os.getcwd()
try:
    os.chdir(tmp_path)
    test_cases = ['react.json', 'configs/react.json']
    for config_name in test_cases:
        result = resolve_config_path(config_name, auto_fetch=False)
        assert result is not None, f'Failed for {config_name}'
        assert result.exists()
        assert result.name == 'react.json'
finally:
    os.chdir(original_cwd)
```

## Next Steps


---

*Source: test_config_fetcher.py:290 | Complexity: Advanced | Last updated: 2026-02-14*