# How To: Skip Codebase Analysis Flag

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test --skip-codebase-analysis CLI flag disables analysis.

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

### Step 1: 'Test --skip-codebase-analysis CLI flag disables analysis.'

```python
'Test --skip-codebase-analysis CLI flag disables analysis.'
```

**Verification:**
```python
assert not github_source['enable_codebase_analysis']
```

### Step 2: Assign config_path = os.path.join(...)

```python
config_path = os.path.join(temp_dir, 'config.json')
```

### Step 3: Assign scraper = UnifiedScraper(...)

```python
scraper = UnifiedScraper(config_path)
```

### Step 4: Assign github_source = value

```python
github_source = scraper.config['sources'][0]
```

**Verification:**
```python
assert not github_source['enable_codebase_analysis']
```

### Step 5: Call json.dump()

```python
json.dump(mock_config, f)
```

### Step 6: Assign unknown = False

```python
source['enable_codebase_analysis'] = False
```


## Complete Example

```python
# Setup
# Fixtures: mock_config, temp_dir

# Workflow
'Test --skip-codebase-analysis CLI flag disables analysis.'
config_path = os.path.join(temp_dir, 'config.json')
with open(config_path, 'w') as f:
    json.dump(mock_config, f)
scraper = UnifiedScraper(config_path)
for source in scraper.config.get('sources', []):
    if source['type'] == 'github':
        source['enable_codebase_analysis'] = False
github_source = scraper.config['sources'][0]
assert not github_source['enable_codebase_analysis']
```

## Next Steps


---

*Source: test_c3_integration.py:160 | Complexity: Intermediate | Last updated: 2026-02-14*