# How To: Creates Subdirectory Per Repo

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that each GitHub repo gets its own subdirectory.

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

### Step 1: 'Test that each GitHub repo gets its own subdirectory.'

```python
'Test that each GitHub repo gets its own subdirectory.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_github_refs', 'description': 'Test', 'sources': []}
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': [], 'github': [{'repo': 'org/repo1', 'repo_id': 'org_repo1', 'data': {'readme': '# Repo 1', 'issues': [], 'releases': [], 'repo_info': {}}}, {'repo': 'org/repo2', 'repo_id': 'org_repo2', 'data': {'readme': '# Repo 2', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Call builder._generate_github_references()

```python
builder._generate_github_references(scraped_data['github'])
```

### Step 6: Assign github_dir = os.path.join(...)

```python
github_dir = os.path.join(builder.skill_dir, 'references', 'github')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo1')))
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo2')))
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that each GitHub repo gets its own subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_github_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'org/repo1', 'repo_id': 'org_repo1', 'data': {'readme': '# Repo 1', 'issues': [], 'releases': [], 'repo_info': {}}}, {'repo': 'org/repo2', 'repo_id': 'org_repo2', 'data': {'readme': '# Repo 2', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
github_dir = os.path.join(builder.skill_dir, 'references', 'github')
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo1')))
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo2')))
```

## Next Steps


---

*Source: test_multi_source.py:269 | Complexity: Advanced | Last updated: 2026-02-14*