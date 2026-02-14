# How To: Init Loads Data

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that converter loads data file on initialization

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

### Step 1: 'Test that converter loads data file on initialization'

```python
'Test that converter loads data file on initialization'
```

### Step 2: Assign config = value

```python
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
```

### Step 3: Assign mock_init.return_value = None

```python
mock_init.return_value = None
```

### Step 4: Assign converter = self.GitHubToSkillConverter(...)

```python
converter = self.GitHubToSkillConverter(config)
```

### Step 5: Assign converter.data_file = str(...)

```python
converter.data_file = str(self.data_file)
```

### Step 6: Assign converter.data = converter._load_data(...)

```python
converter.data = converter._load_data()
```

### Step 7: Call self.assertIn()

```python
self.assertIn('repo_info', converter.data)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(converter.data['repo_info']['name'], 'react')
```


## Complete Example

```python
# Workflow
'Test that converter loads data file on initialization'
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter.__init__') as mock_init:
    mock_init.return_value = None
    converter = self.GitHubToSkillConverter(config)
    converter.data_file = str(self.data_file)
    converter.data = converter._load_data()
    self.assertIn('repo_info', converter.data)
    self.assertEqual(converter.data['repo_info']['name'], 'react')
```

## Next Steps


---

*Source: test_github_scraper.py:596 | Complexity: Advanced | Last updated: 2026-02-14*