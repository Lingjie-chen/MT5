# How To: Creates Readme Per Repo

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that README.md is created for each repo.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `shutil`
- `tempfile`
- `unittest`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`

**Setup Required:**
```python
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)
```

## Step-by-Step Guide

### Step 1: 'Test that README.md is created for each repo.'

```python
'Test that README.md is created for each repo.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_readme', 'description': 'Test', 'sources': []}
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': [], 'github': [{'repo': 'test/myrepo', 'repo_id': 'test_myrepo', 'data': {'readme': '# My Repository\n\nDescription here.', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Call builder._generate_github_references()

```python
builder._generate_github_references(scraped_data['github'])
```

### Step 6: Assign readme_path = os.path.join(...)

```python
readme_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_myrepo', 'README.md')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(readme_path))
```

### Step 8: Assign content = f.read(...)

```python
content = f.read()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('test/myrepo', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that README.md is created for each repo.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_readme', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'test/myrepo', 'repo_id': 'test_myrepo', 'data': {'readme': '# My Repository\n\nDescription here.', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
readme_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_myrepo', 'README.md')
self.assertTrue(os.path.exists(readme_path))
with open(readme_path) as f:
    content = f.read()
    self.assertIn('test/myrepo', content)
```

## Next Steps


---

*Source: test_multi_source.py:299 | Complexity: Advanced | Last updated: 2026-02-14*