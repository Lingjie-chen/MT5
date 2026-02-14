# How To: Github Overhead Within Limits

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that GitHub integration adds ~30-50 lines per skill (not more).

Quality metric: GitHub overhead should be minimal.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: '\n        Test that GitHub integration adds ~30-50 lines per skill (not more).\n\n        Quality metric: GitHub overhead should be minimal.\n        '

```python
'\n        Test that GitHub integration adds ~30-50 lines per skill (not more).\n\n        Quality metric: GitHub overhead should be minimal.\n        '
```

**Verification:**
```python
assert 20 <= github_overhead <= 60, f'GitHub overhead is {github_overhead} lines, expected 20-60'
```

### Step 2: Assign config = value

```python
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://github.com/test/repo', 'categories': {'api': ['api']}}
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
docs_stream = DocsStream(readme='# Test\n\nA short README.', contributing=None, docs_files=[])
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 100, 'forks': 10, 'language': 'Python', 'description': 'Test'}, common_problems=[{'title': 'Issue 1', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['bug']}, {'title': 'Issue 2', 'number': 2, 'state': 'open', 'comments': 3, 'labels': ['bug']}], known_solutions=[], top_labels=[{'label': 'bug', 'count': 10}])
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 8: Assign generator_no_github = RouterGenerator(...)

```python
generator_no_github = RouterGenerator([str(config_path)])
```

### Step 9: Assign skill_md_no_github = generator_no_github.generate_skill_md(...)

```python
skill_md_no_github = generator_no_github.generate_skill_md()
```

### Step 10: Assign lines_no_github = len(...)

```python
lines_no_github = len(skill_md_no_github.split('\n'))
```

### Step 11: Assign generator_with_github = RouterGenerator(...)

```python
generator_with_github = RouterGenerator([str(config_path)], github_streams=github_streams)
```

### Step 12: Assign skill_md_with_github = generator_with_github.generate_skill_md(...)

```python
skill_md_with_github = generator_with_github.generate_skill_md()
```

### Step 13: Assign lines_with_github = len(...)

```python
lines_with_github = len(skill_md_with_github.split('\n'))
```

### Step 14: Assign github_overhead = value

```python
github_overhead = lines_with_github - lines_no_github
```

**Verification:**
```python
assert 20 <= github_overhead <= 60, f'GitHub overhead is {github_overhead} lines, expected 20-60'
```

### Step 15: Call json.dump()

```python
json.dump(config, f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'\n        Test that GitHub integration adds ~30-50 lines per skill (not more).\n\n        Quality metric: GitHub overhead should be minimal.\n        '
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://github.com/test/repo', 'categories': {'api': ['api']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test\n\nA short README.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 100, 'forks': 10, 'language': 'Python', 'description': 'Test'}, common_problems=[{'title': 'Issue 1', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['bug']}, {'title': 'Issue 2', 'number': 2, 'state': 'open', 'comments': 3, 'labels': ['bug']}], known_solutions=[], top_labels=[{'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator_no_github = RouterGenerator([str(config_path)])
skill_md_no_github = generator_no_github.generate_skill_md()
lines_no_github = len(skill_md_no_github.split('\n'))
generator_with_github = RouterGenerator([str(config_path)], github_streams=github_streams)
skill_md_with_github = generator_with_github.generate_skill_md()
lines_with_github = len(skill_md_with_github.split('\n'))
github_overhead = lines_with_github - lines_no_github
assert 20 <= github_overhead <= 60, f'GitHub overhead is {github_overhead} lines, expected 20-60'
```

## Next Steps


---

*Source: test_e2e_three_stream_pipeline.py:407 | Complexity: Advanced | Last updated: 2026-02-14*