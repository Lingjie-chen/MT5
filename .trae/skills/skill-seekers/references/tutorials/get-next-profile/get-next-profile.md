# How To: Get Next Profile

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test profile switching.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `datetime`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.config_manager`
- `skill_seekers.cli.rate_limit_handler`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Test profile switching.'

```python
'Test profile switching.'
```

**Verification:**
```python
assert len(profiles) == 2
```

### Step 2: Assign test_dir = value

```python
test_dir = tmp_path / 'test_switching'
```

**Verification:**
```python
assert next_data is not None
```

### Step 3: Assign config_dir = value

```python
config_dir = test_dir / '.config' / 'skill-seekers'
```

**Verification:**
```python
assert name == 'profile2'
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
```

**Verification:**
```python
assert token == 'ghp_token2'
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
```

**Verification:**
```python
assert next_data is not None
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', test_dir / '.local' / 'share' / 'skill-seekers' / 'progress')
```

**Verification:**
```python
assert name == 'profile1'
```

### Step 7: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'WELCOME_FLAG', config_dir / '.welcomed')
```

**Verification:**
```python
assert token == 'ghp_token1'
```

### Step 8: Assign config = ConfigManager(...)

```python
config = ConfigManager()
```

### Step 9: Assign unknown = value

```python
config.config['github']['profiles'] = {}
```

### Step 10: Call config.add_github_profile()

```python
config.add_github_profile('profile1', 'ghp_token1', set_as_default=True)
```

### Step 11: Call config.add_github_profile()

```python
config.add_github_profile('profile2', 'ghp_token2', set_as_default=False)
```

### Step 12: Assign profiles = config.list_github_profiles(...)

```python
profiles = config.list_github_profiles()
```

**Verification:**
```python
assert len(profiles) == 2
```

### Step 13: Assign next_data = config.get_next_profile(...)

```python
next_data = config.get_next_profile('ghp_token1')
```

**Verification:**
```python
assert next_data is not None
```

### Step 14: Assign unknown = next_data

```python
name, token = next_data
```

**Verification:**
```python
assert name == 'profile2'
```

### Step 15: Assign next_data = config.get_next_profile(...)

```python
next_data = config.get_next_profile('ghp_token2')
```

**Verification:**
```python
assert next_data is not None
```

### Step 16: Assign unknown = next_data

```python
name, token = next_data
```

**Verification:**
```python
assert name == 'profile1'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Test profile switching.'
test_dir = tmp_path / 'test_switching'
config_dir = test_dir / '.config' / 'skill-seekers'
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', test_dir / '.local' / 'share' / 'skill-seekers' / 'progress')
monkeypatch.setattr(ConfigManager, 'WELCOME_FLAG', config_dir / '.welcomed')
config = ConfigManager()
config.config['github']['profiles'] = {}
config.add_github_profile('profile1', 'ghp_token1', set_as_default=True)
config.add_github_profile('profile2', 'ghp_token2', set_as_default=False)
profiles = config.list_github_profiles()
assert len(profiles) == 2
next_data = config.get_next_profile('ghp_token1')
assert next_data is not None
name, token = next_data
assert name == 'profile2'
assert token == 'ghp_token2'
next_data = config.get_next_profile('ghp_token2')
assert next_data is not None
name, token = next_data
assert name == 'profile1'
assert token == 'ghp_token1'
```

## Next Steps


---

*Source: test_rate_limit_handler.py:257 | Complexity: Advanced | Last updated: 2026-02-14*