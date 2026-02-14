# How To: Full Pipeline With Streams

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test complete pipeline with three-stream data.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `skill_seekers.cli.conflict_detector`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test complete pipeline with three-stream data.'

```python
'Test complete pipeline with three-stream data.'
```

**Verification:**
```python
assert 'apis' in result
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': []}
```

**Verification:**
```python
assert 'github_context' in result
```

### Step 3: Assign github_data = value

```python
github_data = {'apis': {}}
```

**Verification:**
```python
assert gh_context['docs']['readme'] == '# Test Project\n\nA test project.'
```

### Step 4: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

**Verification:**
```python
assert gh_context['docs']['contributing'] == '# Contributing\n\nPull requests welcome.'
```

### Step 5: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# Test Project\n\nA test project.', contributing='# Contributing\n\nPull requests welcome.', docs_files=[{'path': 'docs/quickstart.md', 'content': '# Quick Start'}, {'path': 'docs/api.md', 'content': '# API Reference'}])
```

**Verification:**
```python
assert gh_context['docs']['docs_files_count'] == 2
```

### Step 6: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 2500, 'forks': 123, 'language': 'Python', 'description': 'Test framework'}, common_problems=[{'title': 'Installation fails on Windows', 'number': 150, 'state': 'open', 'comments': 25, 'labels': ['bug', 'windows']}, {'title': 'Memory leak in async mode', 'number': 142, 'state': 'open', 'comments': 18, 'labels': ['bug', 'async']}], known_solutions=[{'title': 'Fixed config loading', 'number': 130, 'state': 'closed', 'comments': 8, 'labels': ['bug']}, {'title': 'Resolved OAuth timeout', 'number': 125, 'state': 'closed', 'comments': 12, 'labels': ['oauth']}], top_labels=[{'label': 'bug', 'count': 45}, {'label': 'enhancement', 'count': 20}, {'label': 'question', 'count': 15}])
```

**Verification:**
```python
assert gh_context['metadata']['stars'] == 2500
```

### Step 7: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

**Verification:**
```python
assert gh_context['metadata']['language'] == 'Python'
```

### Step 8: Assign merger = RuleBasedMerger(...)

```python
merger = RuleBasedMerger(docs_data, github_data, [], github_streams)
```

**Verification:**
```python
assert gh_context['issues']['common_problems_count'] == 2
```

### Step 9: Assign result = merger.merge_all(...)

```python
result = merger.merge_all()
```

**Verification:**
```python
assert gh_context['issues']['known_solutions_count'] == 2
```

### Step 10: Assign gh_context = value

```python
gh_context = result['github_context']
```

**Verification:**
```python
assert len(gh_context['issues']['top_problems']) == 2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test complete pipeline with three-stream data.'
docs_data = {'pages': []}
github_data = {'apis': {}}
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test Project\n\nA test project.', contributing='# Contributing\n\nPull requests welcome.', docs_files=[{'path': 'docs/quickstart.md', 'content': '# Quick Start'}, {'path': 'docs/api.md', 'content': '# API Reference'}])
insights_stream = InsightsStream(metadata={'stars': 2500, 'forks': 123, 'language': 'Python', 'description': 'Test framework'}, common_problems=[{'title': 'Installation fails on Windows', 'number': 150, 'state': 'open', 'comments': 25, 'labels': ['bug', 'windows']}, {'title': 'Memory leak in async mode', 'number': 142, 'state': 'open', 'comments': 18, 'labels': ['bug', 'async']}], known_solutions=[{'title': 'Fixed config loading', 'number': 130, 'state': 'closed', 'comments': 8, 'labels': ['bug']}, {'title': 'Resolved OAuth timeout', 'number': 125, 'state': 'closed', 'comments': 12, 'labels': ['oauth']}], top_labels=[{'label': 'bug', 'count': 45}, {'label': 'enhancement', 'count': 20}, {'label': 'question', 'count': 15}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, [], github_streams)
result = merger.merge_all()
assert 'apis' in result
assert 'github_context' in result
gh_context = result['github_context']
assert gh_context['docs']['readme'] == '# Test Project\n\nA test project.'
assert gh_context['docs']['contributing'] == '# Contributing\n\nPull requests welcome.'
assert gh_context['docs']['docs_files_count'] == 2
assert gh_context['metadata']['stars'] == 2500
assert gh_context['metadata']['language'] == 'Python'
assert gh_context['issues']['common_problems_count'] == 2
assert gh_context['issues']['known_solutions_count'] == 2
assert len(gh_context['issues']['top_problems']) == 2
assert len(gh_context['issues']['top_solutions']) == 2
assert len(gh_context['top_labels']) == 3
assert 'conflict_summary' in result
assert result['conflict_summary']['total_conflicts'] == 0
```

## Next Steps


---

*Source: test_merge_sources_github.py:407 | Complexity: Advanced | Last updated: 2026-02-14*