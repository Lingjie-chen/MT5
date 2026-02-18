# How To: Scenario 2 Multi Layer Merge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test multi-layer source merging priority.

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

### Step 1: 'Test multi-layer source merging priority.'

```python
'Test multi-layer source merging priority.'
```

**Verification:**
```python
assert merged is not None
```

### Step 2: Assign source1_data = value

```python
source1_data = {'api': [{'name': 'GoogleProvider', 'params': ['app_id', 'app_secret']}]}
```

**Verification:**
```python
assert isinstance(merged, dict)
```

### Step 3: Assign source2_data = value

```python
source2_data = {'api': [{'name': 'GoogleProvider', 'params': ['client_id', 'client_secret']}]}
```

### Step 4: Assign _github_streams = ThreeStreamData(...)

```python
_github_streams = ThreeStreamData(code_stream=CodeStream(directory=Path('/tmp'), files=[]), docs_stream=DocsStream(readme='Use client_id and client_secret', contributing=None, docs_files=[]), insights_stream=InsightsStream(metadata={'stars': 1000}, common_problems=[{'number': 42, 'title': 'OAuth parameter confusion', 'labels': ['oauth']}], known_solutions=[], top_labels=[]))
```

### Step 5: Assign merger = RuleBasedMerger(...)

```python
merger = RuleBasedMerger(docs_data=source1_data, github_data=source2_data, conflicts=[])
```

### Step 6: Assign merged = merger.merge_all(...)

```python
merged = merger.merge_all()
```

**Verification:**
```python
assert merged is not None
```


## Complete Example

```python
# Workflow
'Test multi-layer source merging priority.'
source1_data = {'api': [{'name': 'GoogleProvider', 'params': ['app_id', 'app_secret']}]}
source2_data = {'api': [{'name': 'GoogleProvider', 'params': ['client_id', 'client_secret']}]}
_github_streams = ThreeStreamData(code_stream=CodeStream(directory=Path('/tmp'), files=[]), docs_stream=DocsStream(readme='Use client_id and client_secret', contributing=None, docs_files=[]), insights_stream=InsightsStream(metadata={'stars': 1000}, common_problems=[{'number': 42, 'title': 'OAuth parameter confusion', 'labels': ['oauth']}], known_solutions=[], top_labels=[]))
merger = RuleBasedMerger(docs_data=source1_data, github_data=source2_data, conflicts=[])
merged = merger.merge_all()
assert merged is not None
assert isinstance(merged, dict)
```

## Next Steps


---

*Source: test_architecture_scenarios.py:597 | Complexity: Intermediate | Last updated: 2026-02-14*