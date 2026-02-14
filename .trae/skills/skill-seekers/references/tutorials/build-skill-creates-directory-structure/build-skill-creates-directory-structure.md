# How To: Build Skill Creates Directory Structure

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that build_skill creates proper directory structure

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `unittest`
- `datetime`
- `pathlib`
- `unittest.mock`
- `github`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`
- `skill_seekers.cli.github_scraper`


## Step-by-Step Guide

### Step 1: 'Test that build_skill creates proper directory structure'

```python
'Test that build_skill creates proper directory structure'
```

### Step 2: Assign data_file_path = value

```python
data_file_path = self.output_dir / 'test_github_data.json'
```

### Step 3: Assign config = value

```python
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
```

### Step 4: Call json.dump()

```python
json.dump(self.mock_data, f)
```

### Step 5: Assign mock_load.return_value = value

```python
mock_load.return_value = self.mock_data
```

### Step 6: Assign converter = self.GitHubToSkillConverter(...)

```python
converter = self.GitHubToSkillConverter(config)
```

### Step 7: Assign converter.skill_dir = str(...)

```python
converter.skill_dir = str(self.output_dir / 'test_skill')
```

### Step 8: Assign converter.data = value

```python
converter.data = self.mock_data
```

### Step 9: Call converter.build_skill()

```python
converter.build_skill()
```

### Step 10: Assign skill_dir = Path(...)

```python
skill_dir = Path(converter.skill_dir)
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(skill_dir.exists())
```

### Step 12: Call self.assertTrue()

```python
self.assertTrue((skill_dir / 'SKILL.md').exists())
```

### Step 13: Call self.assertTrue()

```python
self.assertTrue((skill_dir / 'references').exists())
```


## Complete Example

```python
# Workflow
'Test that build_skill creates proper directory structure'
data_file_path = self.output_dir / 'test_github_data.json'
with open(data_file_path, 'w') as f:
    json.dump(self.mock_data, f)
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter._load_data') as mock_load:
    mock_load.return_value = self.mock_data
    converter = self.GitHubToSkillConverter(config)
    converter.skill_dir = str(self.output_dir / 'test_skill')
    converter.data = self.mock_data
    converter.build_skill()
    skill_dir = Path(converter.skill_dir)
    self.assertTrue(skill_dir.exists())
    self.assertTrue((skill_dir / 'SKILL.md').exists())
    self.assertTrue((skill_dir / 'references').exists())
```

## Next Steps


---

*Source: test_github_scraper.py:610 | Complexity: Advanced | Last updated: 2026-02-14*