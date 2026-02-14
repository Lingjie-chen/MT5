# How To: Generate Subskill Issues Section

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test generation of issues section for sub-skills.

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

### Step 1: 'Test generation of issues section for sub-skills.'

```python
'Test generation of issues section for sub-skills.'
```

**Verification:**
```python
assert 'Common Issues (from GitHub)' in issues_section
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
```

**Verification:**
```python
assert 'OAuth redirect fails' in issues_section
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert 'Issue #50' in issues_section
```

### Step 4: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

**Verification:**
```python
assert '20 comments' in issues_section
```

### Step 5: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
```

**Verification:**
```python
assert '🔴' in issues_section
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth redirect fails', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token expiration issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth']}], known_solutions=[{'title': 'Fixed OAuth flow', 'number': 40, 'state': 'closed', 'comments': 10, 'labels': ['oauth']}], top_labels=[])
```

**Verification:**
```python
assert '✅' in issues_section
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
issues_section = generator.generate_subskill_issues_section('test-oauth', ['oauth'])
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
'Test generation of issues section for sub-skills.'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth redirect fails', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token expiration issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth']}], known_solutions=[{'title': 'Fixed OAuth flow', 'number': 40, 'state': 'closed', 'comments': 10, 'labels': ['oauth']}], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
issues_section = generator.generate_subskill_issues_section('test-oauth', ['oauth'])
assert 'Common Issues (from GitHub)' in issues_section
assert 'OAuth redirect fails' in issues_section
assert 'Issue #50' in issues_section
assert '20 comments' in issues_section
assert '🔴' in issues_section
assert '✅' in issues_section
```

## Next Steps


---

*Source: test_generate_router_github.py:275 | Complexity: Advanced | Last updated: 2026-02-14*