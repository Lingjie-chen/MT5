# How To: Merger Merge All With Streams

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test merge_all() with GitHub streams.

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

### Step 1: 'Test merge_all() with GitHub streams.'

```python
'Test merge_all() with GitHub streams.'
```

**Verification:**
```python
assert 'github_context' in result
```

### Step 2: Assign docs_data = value

```python
docs_data = {'pages': []}
```

**Verification:**
```python
assert 'conflict_summary' in result
```

### Step 3: Assign github_data = value

```python
github_data = {'apis': {}}
```

**Verification:**
```python
assert 'issue_links' in result
```

### Step 4: Assign conflicts = value

```python
conflicts = []
```

**Verification:**
```python
assert result['github_context']['metadata']['stars'] == 500
```

### Step 5: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[])
```

### Step 6: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# README', contributing=None, docs_files=[])
```

### Step 7: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 500}, common_problems=[], known_solutions=[], top_labels=[])
```

### Step 8: Assign github_streams = ThreeStreamData(...)

```python
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

### Step 9: Assign merger = RuleBasedMerger(...)

```python
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
```

### Step 10: Assign result = merger.merge_all(...)

```python
result = merger.merge_all()
```

**Verification:**
```python
assert 'github_context' in result
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test merge_all() with GitHub streams.'
docs_data = {'pages': []}
github_data = {'apis': {}}
conflicts = []
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# README', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 500}, common_problems=[], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
result = merger.merge_all()
assert 'github_context' in result
assert 'conflict_summary' in result
assert 'issue_links' in result
assert result['github_context']['metadata']['stars'] == 500
```

## Next Steps


---

*Source: test_merge_sources_github.py:359 | Complexity: Advanced | Last updated: 2026-02-14*