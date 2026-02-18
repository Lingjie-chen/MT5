# How To: Generate Hybrid Content Basic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic hybrid content generation.

## Prerequisites

**Required Modules:**
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`


## Step-by-Step Guide

### Step 1: 'Test basic hybrid content generation.'

```python
'Test basic hybrid content generation.'
```

**Verification:**
```python
assert 'api_reference' in hybrid
```

### Step 2: Assign api_data = value

```python
api_data = {'apis': {'oauth_login': {'name': 'oauth_login', 'status': 'matched'}}, 'summary': {'total_apis': 1}}
```

**Verification:**
```python
assert 'github_context' in hybrid
```

### Step 3: Assign github_docs = value

```python
github_docs = {'readme': '# Project README', 'contributing': None, 'docs_files': [{'path': 'docs/oauth.md', 'content': 'OAuth guide'}]}
```

**Verification:**
```python
assert 'conflict_summary' in hybrid
```

### Step 4: Assign github_insights = value

```python
github_insights = {'metadata': {'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'Test project'}, 'common_problems': [{'title': 'OAuth fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug']}], 'known_solutions': [{'title': 'Fixed OAuth', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], 'top_labels': [{'label': 'bug', 'count': 10}, {'label': 'enhancement', 'count': 5}]}
```

**Verification:**
```python
assert 'issue_links' in hybrid
```

### Step 5: Assign conflicts = value

```python
conflicts = []
```

**Verification:**
```python
assert hybrid['github_context']['docs']['readme'] == '# Project README'
```

### Step 6: Assign hybrid = generate_hybrid_content(...)

```python
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
```

**Verification:**
```python
assert hybrid['github_context']['docs']['docs_files_count'] == 1
```


## Complete Example

```python
# Workflow
'Test basic hybrid content generation.'
api_data = {'apis': {'oauth_login': {'name': 'oauth_login', 'status': 'matched'}}, 'summary': {'total_apis': 1}}
github_docs = {'readme': '# Project README', 'contributing': None, 'docs_files': [{'path': 'docs/oauth.md', 'content': 'OAuth guide'}]}
github_insights = {'metadata': {'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'Test project'}, 'common_problems': [{'title': 'OAuth fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug']}], 'known_solutions': [{'title': 'Fixed OAuth', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], 'top_labels': [{'label': 'bug', 'count': 10}, {'label': 'enhancement', 'count': 5}]}
conflicts = []
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
assert 'api_reference' in hybrid
assert 'github_context' in hybrid
assert 'conflict_summary' in hybrid
assert 'issue_links' in hybrid
assert hybrid['github_context']['docs']['readme'] == '# Project README'
assert hybrid['github_context']['docs']['docs_files_count'] == 1
assert hybrid['github_context']['metadata']['stars'] == 1234
assert hybrid['github_context']['metadata']['language'] == 'Python'
assert hybrid['github_context']['issues']['common_problems_count'] == 1
assert hybrid['github_context']['issues']['known_solutions_count'] == 1
assert len(hybrid['github_context']['issues']['top_problems']) == 1
assert len(hybrid['github_context']['top_labels']) == 2
```

## Next Steps


---

*Source: test_merge_sources_github.py:133 | Complexity: Intermediate | Last updated: 2026-02-14*