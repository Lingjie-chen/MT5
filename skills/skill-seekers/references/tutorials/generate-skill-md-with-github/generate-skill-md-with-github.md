# How To: Generate Skill Md With Github

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test SKILL.md generation with GitHub metadata.

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

### Step 1: 'Test SKILL.md generation with GitHub metadata.'

```python
'Test SKILL.md generation with GitHub metadata.'
```

**Verification:**
```python
assert '⭐ 5,000' in skill_md
```

### Step 2: Assign config = value

```python
config = {'name': 'test-oauth', 'description': 'OAuth authentication skill', 'base_url': 'https://github.com/test/oauth', 'categories': {'oauth': ['oauth']}}
```

**Verification:**
```python
assert 'Python' in skill_md
```

### Step 3: Assign config_path = value

```python
config_path = tmp_path / 'config.json'
```

**Verification:**
```python
assert 'OAuth 2.0 library' in skill_md
```

### Step 4: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

**Verification:**
```python
assert '## Quick Start' in skill_md
```

### Step 5: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# OAuth Library\n\nQuick start: Install with pip install oauth', contributing=None, docs_files=[])
```

**Verification:**
```python
assert 'OAuth Library' in skill_md
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 5000, 'forks': 200, 'language': 'Python', 'description': 'OAuth 2.0 library'}, common_problems=[{'title': 'Redirect URI mismatch', 'number': 100, 'state': 'open', 'comments': 25, 'labels': ['bug', 'oauth']}, {'title': 'Token refresh fails', 'number': 95, 'state': 'open', 'comments': 18, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
```

**Verification:**
```python
assert '## Common Issues' in skill_md or '## Examples' in skill_md
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

**Verification:**
```python
assert 'how do i handle redirect uri mismatch' in skill_md.lower() or 'how do i fix redirect uri mismatch' in skill_md.lower()
```

### Step 8: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
```

### Step 9: Assign skill_md = generator.generate_skill_md(...)

```python
skill_md = generator.generate_skill_md()
```

**Verification:**
```python
assert '⭐ 5,000' in skill_md
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
'Test SKILL.md generation with GitHub metadata.'
config = {'name': 'test-oauth', 'description': 'OAuth authentication skill', 'base_url': 'https://github.com/test/oauth', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# OAuth Library\n\nQuick start: Install with pip install oauth', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 5000, 'forks': 200, 'language': 'Python', 'description': 'OAuth 2.0 library'}, common_problems=[{'title': 'Redirect URI mismatch', 'number': 100, 'state': 'open', 'comments': 25, 'labels': ['bug', 'oauth']}, {'title': 'Token refresh fails', 'number': 95, 'state': 'open', 'comments': 18, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
skill_md = generator.generate_skill_md()
assert '⭐ 5,000' in skill_md
assert 'Python' in skill_md
assert 'OAuth 2.0 library' in skill_md
assert '## Quick Start' in skill_md
assert 'OAuth Library' in skill_md
assert '## Common Issues' in skill_md or '## Examples' in skill_md
assert 'how do i handle redirect uri mismatch' in skill_md.lower() or 'how do i fix redirect uri mismatch' in skill_md.lower()
```

## Next Steps


---

*Source: test_generate_router_github.py:176 | Complexity: Advanced | Last updated: 2026-02-14*