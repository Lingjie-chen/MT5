# How To: Generate Subskill Issues No Matches

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test issues section when no issues match the topic.

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

### Step 1: 'Test issues section when no issues match the topic.'

```python
'Test issues section when no issues match the topic.'
```

**Verification:**
```python
assert 'Common Issues (from GitHub)' in issues_section
```

### Step 2: Assign config = value

```python
config = {'name': 'test-async', 'base_url': 'https://example.com', 'categories': {'async': ['async']}}
```

**Verification:**
```python
assert 'Other' in issues_section
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert 'OAuth fails' in issues_section
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
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth fails', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 8: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
```

### Step 9: Assign issues_section = generator.generate_subskill_issues_section(...)

```python
issues_section = generator.generate_subskill_issues_section('test-async', ['async'])
```

**Verification:**
```python
assert 'Common Issues (from GitHub)' in issues_section
```

### Step 10: Call json.dump()

```python
json.dump(config, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test issues section when no issues match the topic.'
config = {'name': 'test-async', 'base_url': 'https://example.com', 'categories': {'async': ['async']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth fails', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
issues_section = generator.generate_subskill_issues_section('test-async', ['async'])
assert 'Common Issues (from GitHub)' in issues_section
assert 'Other' in issues_section
assert 'OAuth fails' in issues_section
```

## Next Steps


---

*Source: test_generate_router_github.py:334 | Complexity: Advanced | Last updated: 2026-02-14*