# How To: Codebase Analysis Enabled By Default

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test that enable_codebase_analysis defaults to True.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.config_validator`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_skill_builder`

**Setup Required:**
```python
# Fixtures: mock_config, temp_dir
```

## Step-by-Step Guide

### Step 1: 'Test that enable_codebase_analysis defaults to True.'

```python
'Test that enable_codebase_analysis defaults to True.'
```

**Verification:**
```python
assert github_source.get('enable_codebase_analysis', True)
```

### Step 2: Assign config_without_flag = value

```python
config_without_flag = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'github', 'repo': 'test/repo', 'local_repo_path': temp_dir}]}
```

### Step 3: Assign config_path = os.path.join(...)

```python
config_path = os.path.join(temp_dir, 'config.json')
```

### Step 4: Assign scraper = UnifiedScraper(...)

```python
scraper = UnifiedScraper(config_path)
```

### Step 5: Assign github_source = value

```python
github_source = scraper.config['sources'][0]
```

**Verification:**
```python
assert github_source.get('enable_codebase_analysis', True)
```

### Step 6: Call json.dump()

```python
json.dump(config_without_flag, f)
```


## Complete Example

```python
# Setup
# Fixtures: mock_config, temp_dir

# Workflow
'Test that enable_codebase_analysis defaults to True.'
config_without_flag = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'github', 'repo': 'test/repo', 'local_repo_path': temp_dir}]}
config_path = os.path.join(temp_dir, 'config.json')
with open(config_path, 'w') as f:
    json.dump(config_without_flag, f)
scraper = UnifiedScraper(config_path)
github_source = scraper.config['sources'][0]
assert github_source.get('enable_codebase_analysis', True)
```

## Next Steps


---

*Source: test_c3_integration.py:139 | Complexity: Intermediate | Last updated: 2026-02-14*