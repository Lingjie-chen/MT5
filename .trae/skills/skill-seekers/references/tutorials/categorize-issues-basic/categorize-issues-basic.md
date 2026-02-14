# How To: Categorize Issues Basic

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic issue categorization.

## Prerequisites

**Required Modules:**
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`


## Step-by-Step Guide

### Step 1: 'Test basic issue categorization.'

```python
'Test basic issue categorization.'
```

**Verification:**
```python
assert 'oauth' in categorized
```

### Step 2: Assign problems = value

```python
problems = [{'title': 'OAuth setup fails', 'labels': ['bug', 'oauth'], 'number': 1, 'state': 'open', 'comments': 10}, {'title': 'Testing framework issue', 'labels': ['testing'], 'number': 2, 'state': 'open', 'comments': 5}]
```

**Verification:**
```python
assert len(categorized['oauth']) == 2
```

### Step 3: Assign solutions = value

```python
solutions = [{'title': 'Fixed OAuth redirect', 'labels': ['oauth'], 'number': 3, 'state': 'closed', 'comments': 3}]
```

**Verification:**
```python
assert 'testing' in categorized
```

### Step 4: Assign topics = value

```python
topics = ['oauth', 'testing', 'async']
```

**Verification:**
```python
assert len(categorized['testing']) == 1
```

### Step 5: Assign categorized = categorize_issues_by_topic(...)

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

**Verification:**
```python
assert 'oauth' in categorized
```


## Complete Example

```python
# Workflow
'Test basic issue categorization.'
problems = [{'title': 'OAuth setup fails', 'labels': ['bug', 'oauth'], 'number': 1, 'state': 'open', 'comments': 10}, {'title': 'Testing framework issue', 'labels': ['testing'], 'number': 2, 'state': 'open', 'comments': 5}]
solutions = [{'title': 'Fixed OAuth redirect', 'labels': ['oauth'], 'number': 3, 'state': 'closed', 'comments': 3}]
topics = ['oauth', 'testing', 'async']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized
assert len(categorized['oauth']) == 2
assert 'testing' in categorized
assert len(categorized['testing']) == 1
```

## Next Steps


---

*Source: test_merge_sources_github.py:24 | Complexity: Advanced | Last updated: 2026-02-14*