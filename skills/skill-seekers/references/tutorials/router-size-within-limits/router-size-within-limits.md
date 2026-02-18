# How To: Router Size Within Limits

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that router SKILL.md is ~150 lines (±20).

Quality metric: Router should be concise overview, not exhaustive.

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

### Step 1: '\n        Test that router SKILL.md is ~150 lines (±20).\n\n        Quality metric: Router should be concise overview, not exhaustive.\n        '

```python
'\n        Test that router SKILL.md is ~150 lines (±20).\n\n        Quality metric: Router should be concise overview, not exhaustive.\n        '
```

**Verification:**
```python
assert 60 <= lines <= 250, f'Router is {lines} lines, expected 60-250 for 4 sub-skills'
```

### Step 2: Assign configs = value

```python
configs = []
```

### Step 3: Assign generator = RouterGenerator(...)

```python
generator = RouterGenerator(configs)
```

### Step 4: Assign skill_md = generator.generate_skill_md(...)

```python
skill_md = generator.generate_skill_md()
```

### Step 5: Assign lines = len(...)

```python
lines = len(skill_md.split('\n'))
```

**Verification:**
```python
assert 60 <= lines <= 250, f'Router is {lines} lines, expected 60-250 for 4 sub-skills'
```

### Step 6: Assign config = value

```python
config = {'name': f'test-skill-{i}', 'description': f'Test skill {i}', 'base_url': 'https://github.com/test/repo', 'categories': {f'topic{i}': [f'topic{i}']}}
```

### Step 7: Assign config_path = value

```python
config_path = tmp_path / f'config{i}.json'
```

### Step 8: Call configs.append()

```python
configs.append(str(config_path))
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
'\n        Test that router SKILL.md is ~150 lines (±20).\n\n        Quality metric: Router should be concise overview, not exhaustive.\n        '
configs = []
for i in range(4):
    config = {'name': f'test-skill-{i}', 'description': f'Test skill {i}', 'base_url': 'https://github.com/test/repo', 'categories': {f'topic{i}': [f'topic{i}']}}
    config_path = tmp_path / f'config{i}.json'
    with open(config_path, 'w') as f:
        json.dump(config, f)
    configs.append(str(config_path))
generator = RouterGenerator(configs)
skill_md = generator.generate_skill_md()
lines = len(skill_md.split('\n'))
assert 60 <= lines <= 250, f'Router is {lines} lines, expected 60-250 for 4 sub-skills'
```

## Next Steps


---

*Source: test_e2e_three_stream_pipeline.py:471 | Complexity: Advanced | Last updated: 2026-02-14*