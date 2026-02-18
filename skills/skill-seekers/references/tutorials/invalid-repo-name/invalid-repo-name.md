# How To: Invalid Repo Name

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test handling of invalid repository name

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

### Step 1: 'Test handling of invalid repository name'

```python
'Test handling of invalid repository name'
```

### Step 2: Assign config = value

```python
config = {'repo': 'invalid_repo_format', 'name': 'test', 'github_token': None}
```

### Step 3: Assign scraper = self.GitHubScraper(...)

```python
scraper = self.GitHubScraper(config)
```

### Step 4: Assign scraper.repo = None

```python
scraper.repo = None
```

### Step 5: Assign scraper.github.get_repo = Mock(...)

```python
scraper.github.get_repo = Mock(side_effect=GithubException(404, 'Not found'))
```

### Step 6: Call self.assertIn()

```python
self.assertIn('Repository not found', str(context.exception))
```

### Step 7: Call scraper._fetch_repository()

```python
scraper._fetch_repository()
```


## Complete Example

```python
# Workflow
'Test handling of invalid repository name'
config = {'repo': 'invalid_repo_format', 'name': 'test', 'github_token': None}
with patch('skill_seekers.cli.github_scraper.Github'):
    scraper = self.GitHubScraper(config)
    scraper.repo = None
    scraper.github.get_repo = Mock(side_effect=GithubException(404, 'Not found'))
    with self.assertRaises(ValueError) as context:
        scraper._fetch_repository()
    self.assertIn('Repository not found', str(context.exception))
```

## Next Steps


---

*Source: test_github_scraper.py:980 | Complexity: Advanced | Last updated: 2026-02-14*