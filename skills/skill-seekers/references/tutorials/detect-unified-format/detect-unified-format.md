# How To: Detect Unified Format

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test unified format detection and legacy rejection

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `tempfile`
- `pathlib`
- `pytest`
- `skill_seekers.cli.config_validator`
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_skill_builder`
- `json`
- `tempfile`


## Step-by-Step Guide

### Step 1: 'Test unified format detection and legacy rejection'

```python
'Test unified format detection and legacy rejection'
```

**Verification:**
```python
assert validator.is_unified
```

### Step 2: Assign unified_config = value

```python
unified_config = {'name': 'test', 'description': 'Test skill', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
```

**Verification:**
```python
assert validator.is_unified
```

### Step 3: Assign legacy_config = value

```python
legacy_config = {'name': 'test', 'description': 'Test skill', 'base_url': 'https://example.com'}
```

### Step 4: Call json.dump()

```python
json.dump(unified_config, f)
```

### Step 5: Assign config_path = value

```python
config_path = f.name
```

### Step 6: Assign validator = ConfigValidator(...)

```python
validator = ConfigValidator(config_path)
```

**Verification:**
```python
assert validator.is_unified
```

### Step 7: Call validator.validate()

```python
validator.validate()
```

### Step 8: Call os.unlink()

```python
os.unlink(config_path)
```

### Step 9: Call json.dump()

```python
json.dump(legacy_config, f)
```

### Step 10: Assign config_path = value

```python
config_path = f.name
```

### Step 11: Assign validator = ConfigValidator(...)

```python
validator = ConfigValidator(config_path)
```

**Verification:**
```python
assert validator.is_unified
```

### Step 12: Call os.unlink()

```python
os.unlink(config_path)
```

### Step 13: Call validator.validate()

```python
validator.validate()
```


## Complete Example

```python
# Workflow
'Test unified format detection and legacy rejection'
import json
import tempfile
unified_config = {'name': 'test', 'description': 'Test skill', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
legacy_config = {'name': 'test', 'description': 'Test skill', 'base_url': 'https://example.com'}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(unified_config, f)
    config_path = f.name
try:
    validator = ConfigValidator(config_path)
    assert validator.is_unified
    validator.validate()
finally:
    os.unlink(config_path)
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(legacy_config, f)
    config_path = f.name
try:
    validator = ConfigValidator(config_path)
    assert validator.is_unified
    with pytest.raises(ValueError, match='LEGACY CONFIG FORMAT DETECTED'):
        validator.validate()
finally:
    os.unlink(config_path)
```

## Next Steps


---

*Source: test_unified.py:29 | Complexity: Advanced | Last updated: 2026-02-14*