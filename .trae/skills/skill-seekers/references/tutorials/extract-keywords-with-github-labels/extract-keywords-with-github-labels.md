# How To: Extract Keywords With Github Labels

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test keyword extraction with GitHub issue labels (2x weight).

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

### Step 1: 'Test keyword extraction with GitHub issue labels (2x weight).'

```python
'Test keyword extraction with GitHub issue labels (2x weight).'
```

**Verification:**
```python
assert oauth_count >= 4
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth', 'auth']}}
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

### Step 4: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

### Step 5: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={}, common_problems=[], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 50}, {'label': 'authentication', 'count': 30}, {'label': 'bug', 'count': 20}])
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 8: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
```

### Step 9: Assign routing = generator.extract_routing_keywords(...)

```python
routing = generator.extract_routing_keywords()
```

### Step 10: Assign keywords = value

```python
keywords = routing['test-oauth']
```

### Step 11: Assign oauth_count = keywords.count(...)

```python
oauth_count = keywords.count('oauth')
```

**Verification:**
```python
assert oauth_count >= 4
```

### Step 12: Call json.dump()

```python
json.dump(config, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test keyword extraction with GitHub issue labels (2x weight).'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth', 'auth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 50}, {'label': 'authentication', 'count': 30}, {'label': 'bug', 'count': 20}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
routing = generator.extract_routing_keywords()
keywords = routing['test-oauth']
oauth_count = keywords.count('oauth')
assert oauth_count >= 4
```

## Next Steps


---

*Source: test_generate_router_github.py:141 | Complexity: Advanced | Last updated: 2026-02-14*