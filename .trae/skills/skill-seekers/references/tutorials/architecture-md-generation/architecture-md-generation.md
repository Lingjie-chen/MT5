# How To: Architecture Md Generation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test ARCHITECTURE.md is generated with all 8 sections.

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

### Step 1: 'Test ARCHITECTURE.md is generated with all 8 sections.'

```python
'Test ARCHITECTURE.md is generated with all 8 sections.'
```

**Verification:**
```python
assert os.path.exists(arch_file)
```

### Step 2: Assign github_data = value

```python
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
```

**Verification:**
```python
assert '## 1. Overview' in content
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
```

**Verification:**
```python
assert '## 2. Architectural Patterns' in content
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(mock_config, scraped_data)
```

**Verification:**
```python
assert '## 3. Technology Stack' in content
```

### Step 5: Assign builder.skill_dir = temp_dir

```python
builder.skill_dir = temp_dir
```

**Verification:**
```python
assert '## 4. Design Patterns' in content
```

### Step 6: Assign c3_dir = os.path.join(...)

```python
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
```

**Verification:**
```python
assert '## 5. Configuration Overview' in content
```

### Step 7: Call os.makedirs()

```python
os.makedirs(c3_dir, exist_ok=True)
```

**Verification:**
```python
assert '## 6. Common Workflows' in content
```

### Step 8: Call builder._generate_architecture_overview()

```python
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
```

**Verification:**
```python
assert '## 7. Usage Examples' in content
```

### Step 9: Assign arch_file = os.path.join(...)

```python
arch_file = os.path.join(c3_dir, 'ARCHITECTURE.md')
```

**Verification:**
```python
assert '## 8. Entry Points & Directory Structure' in content
```

### Step 10: Assign content = f.read(...)

```python
content = f.read()
```

**Verification:**
```python
assert 'MVC' in content
```


## Complete Example

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

# Workflow
'Test ARCHITECTURE.md is generated with all 8 sections.'
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
os.makedirs(c3_dir, exist_ok=True)
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
arch_file = os.path.join(c3_dir, 'ARCHITECTURE.md')
assert os.path.exists(arch_file)
with open(arch_file) as f:
    content = f.read()
assert '## 1. Overview' in content
assert '## 2. Architectural Patterns' in content
assert '## 3. Technology Stack' in content
assert '## 4. Design Patterns' in content
assert '## 5. Configuration Overview' in content
assert '## 6. Common Workflows' in content
assert '## 7. Usage Examples' in content
assert '## 8. Entry Points & Directory Structure' in content
assert 'MVC' in content
assert 'Flask' in content
assert 'Factory' in content
assert '15 usage example(s)' in content or '15 total' in content
assert 'Security Alert' in content
```

## Next Steps


---

*Source: test_c3_integration.py:179 | Complexity: Advanced | Last updated: 2026-02-14*