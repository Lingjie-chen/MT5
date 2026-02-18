# How To: Match Issues To Apis Basic

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic issue to API matching.

## Prerequisites

**Required Modules:**
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`

**Required Fixtures:**
- `api_client` fixture


## Step-by-Step Guide

### Step 1: 'Test basic issue to API matching.'

```python
'Test basic issue to API matching.'
```

**Verification:**
```python
assert 'oauth_login' in issue_links
```

### Step 2: Assign apis = value

```python
apis = {'oauth_login': {'name': 'oauth_login'}, 'async_fetch': {'name': 'async_fetch'}}
```

**Verification:**
```python
assert len(issue_links['oauth_login']) == 1
```

### Step 3: Assign problems = value

```python
problems = [{'title': 'OAuth login fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug', 'oauth']}]
```

**Verification:**
```python
assert issue_links['oauth_login'][0]['number'] == 42
```

### Step 4: Assign solutions = value

```python
solutions = [{'title': 'Fixed async fetch timeout', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['async']}]
```

**Verification:**
```python
assert 'async_fetch' in issue_links
```

### Step 5: Assign issue_links = _match_issues_to_apis(...)

```python
issue_links = _match_issues_to_apis(apis, problems, solutions)
```

**Verification:**
```python
assert len(issue_links['async_fetch']) == 1
```


## Complete Example

```python
# Workflow
'Test basic issue to API matching.'
apis = {'oauth_login': {'name': 'oauth_login'}, 'async_fetch': {'name': 'async_fetch'}}
problems = [{'title': 'OAuth login fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug', 'oauth']}]
solutions = [{'title': 'Fixed async fetch timeout', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['async']}]
issue_links = _match_issues_to_apis(apis, problems, solutions)
assert 'oauth_login' in issue_links
assert len(issue_links['oauth_login']) == 1
assert issue_links['oauth_login'][0]['number'] == 42
assert 'async_fetch' in issue_links
assert len(issue_links['async_fetch']) == 1
assert issue_links['async_fetch'][0]['number'] == 35
```

## Next Steps


---

*Source: test_merge_sources_github.py:246 | Complexity: Advanced | Last updated: 2026-02-14*