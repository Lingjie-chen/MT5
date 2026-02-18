# How To: Infer Router Name

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test router name inference from sub-skill names.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test router name inference from sub-skill names.'

```python
'Test router name inference from sub-skill names.'
```

**Verification:**
```python
assert generator.router_name == 'fastmcp'
```

### Step 2: Assign config1 = value

```python
config1 = {'name': 'fastmcp-oauth', 'base_url': 'https://example.com'}
```

### Step 3: Assign config2 = value

```python
config2 = {'name': 'fastmcp-async', 'base_url': 'https://example.com'}
```

### Step 4: Assign config_path1 = value

```python
config_path1 = tmp_path / 'config1.json'
```

### Step 5: Assign config_path2 = value

```python
config_path2 = tmp_path / 'config2.json'
```

### Step 6: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path1), str(config_path2)])
```

**Verification:**
```python
assert generator.router_name == 'fastmcp'
```

### Step 7: Call json.dump()

```python
json.dump(config1, f)
```

### Step 8: Call json.dump()

```python
json.dump(config2, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test router name inference from sub-skill names.'
config1 = {'name': 'fastmcp-oauth', 'base_url': 'https://example.com'}
config2 = {'name': 'fastmcp-async', 'base_url': 'https://example.com'}
config_path1 = tmp_path / 'config1.json'
config_path2 = tmp_path / 'config2.json'
with open(config_path1, 'w') as f:
    json.dump(config1, f)
with open(config_path2, 'w') as f:
    json.dump(config2, f)
generator = RouterGenerator([str(config_path1), str(config_path2)])
assert generator.router_name == 'fastmcp'
```

## Next Steps


---

*Source: test_generate_router_github.py:51 | Complexity: Advanced | Last updated: 2026-02-14*