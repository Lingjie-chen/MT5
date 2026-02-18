# How To: C3 Reference Directory Structure

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test correct C3.x reference directory structure is created.

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
# Fixtures: mock_config, mock_c3_data, temp_dir
```

## Step-by-Step Guide

### Step 1: 'Test correct C3.x reference directory structure is created.'

```python
'Test correct C3.x reference directory structure is created.'
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'ARCHITECTURE.md'))
```

### Step 2: Assign github_data = value

```python
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'patterns'))
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'examples'))
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(mock_config, scraped_data)
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'guides'))
```

### Step 5: Assign builder.skill_dir = temp_dir

```python
builder.skill_dir = temp_dir
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'configuration'))
```

### Step 6: Assign c3_dir = os.path.join(...)

```python
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'architecture_details'))
```

### Step 7: Call os.makedirs()

```python
os.makedirs(c3_dir, exist_ok=True)
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'index.md'))
```

### Step 8: Call builder._generate_architecture_overview()

```python
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'examples', 'index.md'))
```

### Step 9: Call builder._generate_pattern_references()

```python
builder._generate_pattern_references(c3_dir, mock_c3_data.get('patterns'))
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'guides', 'index.md'))
```

### Step 10: Call builder._generate_example_references()

```python
builder._generate_example_references(c3_dir, mock_c3_data.get('test_examples'))
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'configuration', 'index.md'))
```

### Step 11: Call builder._generate_guide_references()

```python
builder._generate_guide_references(c3_dir, mock_c3_data.get('how_to_guides'))
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'architecture_details', 'index.md'))
```

### Step 12: Call builder._generate_config_references()

```python
builder._generate_config_references(c3_dir, mock_c3_data.get('config_patterns'))
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'detected_patterns.json'))
```

### Step 13: Call builder._copy_architecture_details()

```python
builder._copy_architecture_details(c3_dir, mock_c3_data.get('architecture'))
```

**Verification:**
```python
assert os.path.exists(os.path.join(c3_dir, 'examples', 'test_examples.json'))
```


## Complete Example

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

# Workflow
'Test correct C3.x reference directory structure is created.'
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
os.makedirs(c3_dir, exist_ok=True)
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
builder._generate_pattern_references(c3_dir, mock_c3_data.get('patterns'))
builder._generate_example_references(c3_dir, mock_c3_data.get('test_examples'))
builder._generate_guide_references(c3_dir, mock_c3_data.get('how_to_guides'))
builder._generate_config_references(c3_dir, mock_c3_data.get('config_patterns'))
builder._copy_architecture_details(c3_dir, mock_c3_data.get('architecture'))
assert os.path.exists(os.path.join(c3_dir, 'ARCHITECTURE.md'))
assert os.path.exists(os.path.join(c3_dir, 'patterns'))
assert os.path.exists(os.path.join(c3_dir, 'examples'))
assert os.path.exists(os.path.join(c3_dir, 'guides'))
assert os.path.exists(os.path.join(c3_dir, 'configuration'))
assert os.path.exists(os.path.join(c3_dir, 'architecture_details'))
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'examples', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'guides', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'configuration', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'architecture_details', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'detected_patterns.json'))
assert os.path.exists(os.path.join(c3_dir, 'examples', 'test_examples.json'))
assert os.path.exists(os.path.join(c3_dir, 'configuration', 'config_patterns.json'))
```

## Next Steps


---

*Source: test_c3_integration.py:220 | Complexity: Advanced | Last updated: 2026-02-14*