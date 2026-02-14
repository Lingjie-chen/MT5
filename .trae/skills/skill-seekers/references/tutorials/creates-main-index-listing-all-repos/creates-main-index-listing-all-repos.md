# How To: Creates Main Index Listing All Repos

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that main index.md lists all GitHub repositories.

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

### Step 1: 'Test that main index.md lists all GitHub repositories.'

```python
'Test that main index.md lists all GitHub repositories.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_github_index', 'description': 'Test', 'sources': []}
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': [], 'github': [{'repo': 'org/first', 'repo_id': 'org_first', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 100}}}, {'repo': 'org/second', 'repo_id': 'org_second', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 50}}}], 'pdf': []}
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Call builder._generate_github_references()

```python
builder._generate_github_references(scraped_data['github'])
```

### Step 6: Assign main_index = os.path.join(...)

```python
main_index = os.path.join(builder.skill_dir, 'references', 'github', 'index.md')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(main_index))
```

### Step 8: Assign content = f.read(...)

```python
content = f.read()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('org/first', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('org/second', content)
```

### Step 11: Call self.assertIn()

```python
self.assertIn('2 GitHub repositories', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that main index.md lists all GitHub repositories.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_github_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'org/first', 'repo_id': 'org_first', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 100}}}, {'repo': 'org/second', 'repo_id': 'org_second', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 50}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
main_index = os.path.join(builder.skill_dir, 'references', 'github', 'index.md')
self.assertTrue(os.path.exists(main_index))
with open(main_index) as f:
    content = f.read()
    self.assertIn('org/first', content)
    self.assertIn('org/second', content)
    self.assertIn('2 GitHub repositories', content)
```

## Next Steps


---

*Source: test_multi_source.py:385 | Complexity: Advanced | Last updated: 2026-02-14*