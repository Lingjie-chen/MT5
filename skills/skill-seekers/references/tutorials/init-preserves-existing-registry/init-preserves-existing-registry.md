# How To: Init Preserves Existing Registry

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that initialization doesn't overwrite existing registry.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `pytest`
- `skill_seekers.mcp.source_manager`

**Setup Required:**
```python
# Fixtures: temp_config_dir
```

## Step-by-Step Guide

### Step 1: "Test that initialization doesn't overwrite existing registry."

```python
"Test that initialization doesn't overwrite existing registry."
```

**Verification:**
```python
assert len(data['sources']) == 1
```

### Step 2: Assign registry_file = value

```python
registry_file = temp_config_dir / 'sources.json'
```

### Step 3: Assign existing_data = value

```python
existing_data = {'version': '1.0', 'sources': [{'name': 'test', 'git_url': 'https://example.com/repo.git'}]}
```

### Step 4: Assign _manager = SourceManager(...)

```python
_manager = SourceManager(config_dir=str(temp_config_dir))
```

### Step 5: Call json.dump()

```python
json.dump(existing_data, f)
```

### Step 6: Assign data = json.load(...)

```python
data = json.load(f)
```

**Verification:**
```python
assert len(data['sources']) == 1
```


## Complete Example

```python
# Setup
# Fixtures: temp_config_dir

# Workflow
"Test that initialization doesn't overwrite existing registry."
registry_file = temp_config_dir / 'sources.json'
existing_data = {'version': '1.0', 'sources': [{'name': 'test', 'git_url': 'https://example.com/repo.git'}]}
with open(registry_file, 'w') as f:
    json.dump(existing_data, f)
_manager = SourceManager(config_dir=str(temp_config_dir))
with open(registry_file) as f:
    data = json.load(f)
    assert len(data['sources']) == 1
```

## Next Steps


---

*Source: test_source_manager.py:51 | Complexity: Advanced | Last updated: 2026-02-14*