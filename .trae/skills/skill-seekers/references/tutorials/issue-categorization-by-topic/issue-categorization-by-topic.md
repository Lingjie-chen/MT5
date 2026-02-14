# How To: Issue Categorization By Topic

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that issues are correctly categorized by topic keywords.

## Prerequisites

**Required Modules:**
- `json`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`


## Step-by-Step Guide

### Step 1: 'Test that issues are correctly categorized by topic keywords.'

```python
'Test that issues are correctly categorized by topic keywords.'
```

**Verification:**
```python
assert 'oauth' in categorized or 'auth' in categorized or 'authentication' in categorized
```

### Step 2: Assign problems = value

```python
problems = [{'title': 'OAuth fails on redirect', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token refresh issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth', 'token']}, {'title': 'Async deadlock', 'number': 40, 'state': 'open', 'comments': 12, 'labels': ['async', 'bug']}, {'title': 'Database connection lost', 'number': 35, 'state': 'open', 'comments': 10, 'labels': ['database']}]
```

**Verification:**
```python
assert len(oauth_issues) >= 2
```

### Step 3: Assign solutions = value

```python
solutions = [{'title': 'Fixed OAuth flow', 'number': 30, 'state': 'closed', 'comments': 8, 'labels': ['oauth']}, {'title': 'Resolved async race', 'number': 25, 'state': 'closed', 'comments': 6, 'labels': ['async']}]
```

**Verification:**
```python
assert any(('OAuth' in title for title in oauth_titles))
```

### Step 4: Assign topics = value

```python
topics = ['oauth', 'auth', 'authentication']
```

### Step 5: Assign categorized = categorize_issues_by_topic(...)

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

**Verification:**
```python
assert 'oauth' in categorized or 'auth' in categorized or 'authentication' in categorized
```

### Step 6: Assign oauth_issues = value

```python
oauth_issues = categorized.get('oauth', []) + categorized.get('auth', []) + categorized.get('authentication', [])
```

**Verification:**
```python
assert len(oauth_issues) >= 2
```

### Step 7: Assign oauth_titles = value

```python
oauth_titles = [issue['title'] for issue in oauth_issues]
```

**Verification:**
```python
assert any(('OAuth' in title for title in oauth_titles))
```


## Complete Example

```python
# Workflow
'Test that issues are correctly categorized by topic keywords.'
problems = [{'title': 'OAuth fails on redirect', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token refresh issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth', 'token']}, {'title': 'Async deadlock', 'number': 40, 'state': 'open', 'comments': 12, 'labels': ['async', 'bug']}, {'title': 'Database connection lost', 'number': 35, 'state': 'open', 'comments': 10, 'labels': ['database']}]
solutions = [{'title': 'Fixed OAuth flow', 'number': 30, 'state': 'closed', 'comments': 8, 'labels': ['oauth']}, {'title': 'Resolved async race', 'number': 25, 'state': 'closed', 'comments': 6, 'labels': ['async']}]
topics = ['oauth', 'auth', 'authentication']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized or 'auth' in categorized or 'authentication' in categorized
oauth_issues = categorized.get('oauth', []) + categorized.get('auth', []) + categorized.get('authentication', [])
assert len(oauth_issues) >= 2
oauth_titles = [issue['title'] for issue in oauth_issues]
assert any(('OAuth' in title for title in oauth_titles))
```

## Next Steps


---

*Source: test_e2e_three_stream_pipeline.py:154 | Complexity: Advanced | Last updated: 2026-02-14*