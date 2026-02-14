# How To: Extract Routing Keywords Basic

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic keyword extraction without GitHub.

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

### Step 1: 'Test basic keyword extraction without GitHub.'

```python
'Test basic keyword extraction without GitHub.'
```

**Verification:**
```python
assert 'test-oauth' in routing
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'authentication': ['auth', 'oauth'], 'tokens': ['token', 'jwt']}}
```

**Verification:**
```python
assert 'authentication' in keywords
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert 'tokens' in keywords
```

### Step 4: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)])
```

**Verification:**
```python
assert 'oauth' in keywords
```

### Step 5: Assign routing = generator.extract_routing_keywords(...)

```python
routing = generator.extract_routing_keywords()
```

**Verification:**
```python
assert 'test-oauth' in routing
```

### Step 6: Assign keywords = value

```python
keywords = routing['test-oauth']
```

**Verification:**
```python
assert 'authentication' in keywords
```

### Step 7: Call json.dump()

```python
json.dump(config, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test basic keyword extraction without GitHub.'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'authentication': ['auth', 'oauth'], 'tokens': ['token', 'jwt']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
routing = generator.extract_routing_keywords()
assert 'test-oauth' in routing
keywords = routing['test-oauth']
assert 'authentication' in keywords
assert 'tokens' in keywords
assert 'oauth' in keywords
```

## Next Steps


---

*Source: test_generate_router_github.py:68 | Complexity: Intermediate | Last updated: 2026-02-14*