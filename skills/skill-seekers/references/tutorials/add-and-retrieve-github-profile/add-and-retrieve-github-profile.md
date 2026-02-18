# How To: Add And Retrieve Github Profile

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test adding and retrieving GitHub profiles.

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

### Step 1: 'Test adding and retrieving GitHub profiles.'

```python
'Test adding and retrieving GitHub profiles.'
```

**Verification:**
```python
assert token == 'ghp_test123'
```

### Step 2: Assign config_dir = value

```python
config_dir = tmp_path / '.config' / 'skill-seekers'
```

**Verification:**
```python
assert len(profiles) == 1
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
```

**Verification:**
```python
assert profiles[0]['is_default'] is True
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
```

**Verification:**
```python
assert profiles[0]['name'] == 'test-profile'
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', tmp_path / '.local' / 'share' / 'skill-seekers' / 'progress')
```

### Step 6: Assign config = ConfigManager(...)

```python
config = ConfigManager()
```

### Step 7: Call config.add_github_profile()

```python
config.add_github_profile(name='test-profile', token='ghp_test123', description='Test profile', rate_limit_strategy='wait', timeout_minutes=45, set_as_default=True)
```

### Step 8: Assign token = config.get_github_token(...)

```python
token = config.get_github_token(profile_name='test-profile')
```

**Verification:**
```python
assert token == 'ghp_test123'
```

### Step 9: Assign profiles = config.list_github_profiles(...)

```python
profiles = config.list_github_profiles()
```

**Verification:**
```python
assert len(profiles) == 1
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Test adding and retrieving GitHub profiles.'
config_dir = tmp_path / '.config' / 'skill-seekers'
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', tmp_path / '.local' / 'share' / 'skill-seekers' / 'progress')
config = ConfigManager()
config.add_github_profile(name='test-profile', token='ghp_test123', description='Test profile', rate_limit_strategy='wait', timeout_minutes=45, set_as_default=True)
token = config.get_github_token(profile_name='test-profile')
assert token == 'ghp_test123'
profiles = config.list_github_profiles()
assert len(profiles) == 1
assert profiles[0]['is_default'] is True
assert profiles[0]['name'] == 'test-profile'
```

## Next Steps


---

*Source: test_rate_limit_handler.py:224 | Complexity: Advanced | Last updated: 2026-02-14*