# How To: Merger With Github Streams

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test merger with three-stream GitHub data.

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

### Step 1: 'Test merger with three-stream GitHub data.'

```python
'Test merger with three-stream GitHub data.'
```

**Verification:**
```python
assert merger.github_streams is not None
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': []}
```

**Verification:**
```python
assert merger.github_docs is not None
```

### Step 3: Assign github_data = value

```python
github_data = {'apis': {}}
```

**Verification:**
```python
assert merger.github_insights is not None
```

### Step 4: Assign conflicts = value

```python
conflicts = []
```

**Verification:**
```python
assert merger.github_docs['readme'] == '# README'
```

### Step 5: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

**Verification:**
```python
assert merger.github_insights['metadata']['stars'] == 1234
```

### Step 6: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# README', contributing='# Contributing', docs_files=[{'path': 'docs/guide.md', 'content': 'Guide content'}])
```

### Step 7: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python'}, common_problems=[{'title': 'Bug 1', 'number': 1, 'state': 'open', 'comments': 10, 'labels': ['bug']}], known_solutions=[{'title': 'Fix 1', 'number': 2, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], top_labels=[{'label': 'bug', 'count': 10}])
```

### Step 8: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 9: Assign merger = RuleBasedMerger(...)

```python
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
```

**Verification:**
```python
assert merger.github_streams is not None
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test merger with three-stream GitHub data.'
docs_data = {'pages': []}
github_data = {'apis': {}}
conflicts = []
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# README', contributing='# Contributing', docs_files=[{'path': 'docs/guide.md', 'content': 'Guide content'}])
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python'}, common_problems=[{'title': 'Bug 1', 'number': 1, 'state': 'open', 'comments': 10, 'labels': ['bug']}], known_solutions=[{'title': 'Fix 1', 'number': 2, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], top_labels=[{'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
assert merger.github_streams is not None
assert merger.github_docs is not None
assert merger.github_insights is not None
assert merger.github_docs['readme'] == '# README'
assert merger.github_insights['metadata']['stars'] == 1234
```

## Next Steps


---

*Source: test_merge_sources_github.py:325 | Complexity: Advanced | Last updated: 2026-02-14*