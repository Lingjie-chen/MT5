# How To: Temp Git Repo

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Create a temporary git repository with sample configs.

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `pathlib`
- `git`
- `pytest`
- `skill_seekers.mcp.git_repo`
- `skill_seekers.mcp.source_manager`
- `mcp`
- `mcp.types`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`
- `skill_seekers.mcp.server`


## Step-by-Step Guide

### Step 1: 'Create a temporary git repository with sample configs.'

```python
'Create a temporary git repository with sample configs.'
```

### Step 2: Assign repo_dir = tempfile.mkdtemp(...)

```python
repo_dir = tempfile.mkdtemp(prefix='ss_repo_')
```

### Step 3: Assign repo = git.Repo.init(...)

```python
repo = git.Repo.init(repo_dir)
```

### Step 4: Assign configs = value

```python
configs = {'react.json': {'name': 'react', 'description': 'React framework for UIs', 'base_url': 'https://react.dev/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {'getting_started': ['learn', 'start'], 'api': ['reference', 'api']}, 'rate_limit': 0.5, 'max_pages': 100}, 'vue.json': {'name': 'vue', 'description': 'Vue.js progressive framework', 'base_url': 'https://vuejs.org/', 'selectors': {'main_content': 'main', 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 50}, 'django.json': {'name': 'django', 'description': 'Django web framework', 'base_url': 'https://docs.djangoproject.com/', 'selectors': {'main_content': "div[role='main']", 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 200}}
```

### Step 5: Call repo.index.add()

```python
repo.index.add(['*.json'])
```

### Step 6: Call repo.index.commit()

```python
repo.index.commit('Initial commit with sample configs')
```

### Step 7: yield (repo_dir, repo)

```python
yield (repo_dir, repo)
```

### Step 8: Call shutil.rmtree()

```python
shutil.rmtree(repo_dir, ignore_errors=True)
```

### Step 9: Assign config_path = value

```python
config_path = Path(repo_dir) / filename
```

### Step 10: Call json.dump()

```python
json.dump(config_data, f, indent=2)
```


## Complete Example

```python
# Workflow
'Create a temporary git repository with sample configs.'
repo_dir = tempfile.mkdtemp(prefix='ss_repo_')
repo = git.Repo.init(repo_dir)
configs = {'react.json': {'name': 'react', 'description': 'React framework for UIs', 'base_url': 'https://react.dev/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {'getting_started': ['learn', 'start'], 'api': ['reference', 'api']}, 'rate_limit': 0.5, 'max_pages': 100}, 'vue.json': {'name': 'vue', 'description': 'Vue.js progressive framework', 'base_url': 'https://vuejs.org/', 'selectors': {'main_content': 'main', 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 50}, 'django.json': {'name': 'django', 'description': 'Django web framework', 'base_url': 'https://docs.djangoproject.com/', 'selectors': {'main_content': "div[role='main']", 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 200}}
for filename, config_data in configs.items():
    config_path = Path(repo_dir) / filename
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
repo.index.add(['*.json'])
repo.index.commit('Initial commit with sample configs')
yield (repo_dir, repo)
shutil.rmtree(repo_dir, ignore_errors=True)
```

## Next Steps


---

*Source: test_git_sources_e2e.py:51 | Complexity: Advanced | Last updated: 2026-02-14*