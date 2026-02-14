# How To: Scenario 2 Issue Categorization

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test categorizing GitHub issues by topic.

## Prerequisites

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`


## Step-by-Step Guide

### Step 1: 'Test categorizing GitHub issues by topic.'

```python
'Test categorizing GitHub issues by topic.'
```

**Verification:**
```python
assert 'oauth' in categorized
```

### Step 2: Assign problems = value

```python
problems = [{'number': 42, 'title': 'OAuth setup fails', 'labels': ['oauth', 'bug']}, {'number': 38, 'title': 'Async tools not working', 'labels': ['async', 'question']}, {'number': 35, 'title': 'Testing with pytest', 'labels': ['testing', 'question']}, {'number': 30, 'title': 'Google OAuth redirect', 'labels': ['oauth', 'question']}]
```

**Verification:**
```python
assert 'async' in categorized
```

### Step 3: Assign solutions = value

```python
solutions = [{'number': 25, 'title': 'Fixed OAuth redirect', 'labels': ['oauth', 'bug']}, {'number': 20, 'title': 'Async timeout solution', 'labels': ['async', 'bug']}]
```

**Verification:**
```python
assert 'testing' in categorized
```

### Step 4: Assign topics = value

```python
topics = ['oauth', 'async', 'testing']
```

**Verification:**
```python
assert len(oauth_issues) >= 2
```

### Step 5: Assign categorized = categorize_issues_by_topic(...)

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

**Verification:**
```python
assert 42 in oauth_numbers
```

### Step 6: Assign oauth_issues = value

```python
oauth_issues = categorized['oauth']
```

**Verification:**
```python
assert len(async_issues) >= 2
```

### Step 7: Assign oauth_numbers = value

```python
oauth_numbers = [i['number'] for i in oauth_issues]
```

**Verification:**
```python
assert 38 in async_numbers
```

### Step 8: Assign async_issues = value

```python
async_issues = categorized['async']
```

**Verification:**
```python
assert len(testing_issues) >= 1
```

### Step 9: Assign async_numbers = value

```python
async_numbers = [i['number'] for i in async_issues]
```

**Verification:**
```python
assert 38 in async_numbers
```

### Step 10: Assign testing_issues = value

```python
testing_issues = categorized['testing']
```

**Verification:**
```python
assert len(testing_issues) >= 1
```


## Complete Example

```python
# Workflow
'Test categorizing GitHub issues by topic.'
problems = [{'number': 42, 'title': 'OAuth setup fails', 'labels': ['oauth', 'bug']}, {'number': 38, 'title': 'Async tools not working', 'labels': ['async', 'question']}, {'number': 35, 'title': 'Testing with pytest', 'labels': ['testing', 'question']}, {'number': 30, 'title': 'Google OAuth redirect', 'labels': ['oauth', 'question']}]
solutions = [{'number': 25, 'title': 'Fixed OAuth redirect', 'labels': ['oauth', 'bug']}, {'number': 20, 'title': 'Async timeout solution', 'labels': ['async', 'bug']}]
topics = ['oauth', 'async', 'testing']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized
assert 'async' in categorized
assert 'testing' in categorized
oauth_issues = categorized['oauth']
assert len(oauth_issues) >= 2
oauth_numbers = [i['number'] for i in oauth_issues]
assert 42 in oauth_numbers
async_issues = categorized['async']
assert len(async_issues) >= 2
async_numbers = [i['number'] for i in async_issues]
assert 38 in async_numbers
testing_issues = categorized['testing']
assert len(testing_issues) >= 1
```

## Next Steps


---

*Source: test_architecture_scenarios.py:519 | Complexity: Advanced | Last updated: 2026-02-14*