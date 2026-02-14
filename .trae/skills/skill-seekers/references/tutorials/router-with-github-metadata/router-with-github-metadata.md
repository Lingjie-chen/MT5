# How To: Router With Github Metadata

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test router generator with GitHub metadata.

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

### Step 1: 'Test router generator with GitHub metadata.'

```python
'Test router generator with GitHub metadata.'
```

**Verification:**
```python
assert generator.github_metadata is not None
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://github.com/test/repo', 'categories': {'oauth': ['oauth', 'auth']}}
```

**Verification:**
```python
assert generator.github_metadata['stars'] == 1234
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert generator.github_docs is not None
```

### Step 4: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

**Verification:**
```python
assert generator.github_docs['readme'].startswith('# Test Project')
```

### Step 5: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# Test Project\n\nA test OAuth library.', contributing=None, docs_files=[])
```

**Verification:**
```python
assert generator.github_issues is not None
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'OAuth helper'}, common_problems=[{'title': 'OAuth fails on redirect', 'number': 42, 'state': 'open', 'comments': 15, 'labels': ['bug', 'oauth']}], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 20}, {'label': 'bug', 'count': 10}])
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 8: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
```

**Verification:**
```python
assert generator.github_metadata is not None
```

### Step 9: Call json.dump()

```python
json.dump(config, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test router generator with GitHub metadata.'
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://github.com/test/repo', 'categories': {'oauth': ['oauth', 'auth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test Project\n\nA test OAuth library.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'OAuth helper'}, common_problems=[{'title': 'OAuth fails on redirect', 'number': 42, 'state': 'open', 'comments': 15, 'labels': ['bug', 'oauth']}], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 20}, {'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
assert generator.github_metadata is not None
assert generator.github_metadata['stars'] == 1234
assert generator.github_docs is not None
assert generator.github_docs['readme'].startswith('# Test Project')
assert generator.github_issues is not None
```

## Next Steps


---

*Source: test_generate_router_github.py:93 | Complexity: Advanced | Last updated: 2026-02-14*