# How To: Creates Issues File When Issues Exist

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that issues.md is created when repo has issues.

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

### Step 1: 'Test that issues.md is created when repo has issues.'

```python
'Test that issues.md is created when repo has issues.'
```

### Step 2: Assign config = value

```python
config = {'name': 'test_issues', 'description': 'Test', 'sources': []}
```

### Step 3: Assign scraped_data = value

```python
scraped_data = {'documentation': [], 'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'data': {'readme': '# Repo', 'issues': [{'number': 1, 'title': 'Bug report', 'state': 'open', 'labels': ['bug'], 'url': 'https://github.com/test/repo/issues/1'}, {'number': 2, 'title': 'Feature request', 'state': 'closed', 'labels': ['enhancement'], 'url': 'https://github.com/test/repo/issues/2'}], 'releases': [], 'repo_info': {}}}], 'pdf': []}
```

### Step 4: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 5: Call builder._generate_github_references()

```python
builder._generate_github_references(scraped_data['github'])
```

### Step 6: Assign issues_path = os.path.join(...)

```python
issues_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_repo', 'issues.md')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(issues_path))
```

### Step 8: Assign content = f.read(...)

```python
content = f.read()
```

### Step 9: Call self.assertIn()

```python
self.assertIn('Bug report', content)
```

### Step 10: Call self.assertIn()

```python
self.assertIn('Feature request', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that issues.md is created when repo has issues.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_issues', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'data': {'readme': '# Repo', 'issues': [{'number': 1, 'title': 'Bug report', 'state': 'open', 'labels': ['bug'], 'url': 'https://github.com/test/repo/issues/1'}, {'number': 2, 'title': 'Feature request', 'state': 'closed', 'labels': ['enhancement'], 'url': 'https://github.com/test/repo/issues/2'}], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
issues_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_repo', 'issues.md')
self.assertTrue(os.path.exists(issues_path))
with open(issues_path) as f:
    content = f.read()
    self.assertIn('Bug report', content)
    self.assertIn('Feature request', content)
```

## Next Steps


---

*Source: test_multi_source.py:334 | Complexity: Advanced | Last updated: 2026-02-14*