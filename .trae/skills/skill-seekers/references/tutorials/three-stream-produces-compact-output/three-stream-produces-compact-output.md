# How To: Three Stream Produces Compact Output

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that three-stream architecture produces compact, efficient output.

This is a qualitative test - we verify that output is structured and
not duplicated across streams.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: '\n        Test that three-stream architecture produces compact, efficient output.\n\n        This is a qualitative test - we verify that output is structured and\n        not duplicated across streams.\n        '

```python
'\n        Test that three-stream architecture produces compact, efficient output.\n\n        This is a qualitative test - we verify that output is structured and\n        not duplicated across streams.\n        '
```

**Verification:**
```python
assert code_stream.directory == tmp_path
```

### Step 2: Call unknown.write_text()

```python
(tmp_path / 'main.py').write_text("import os\nprint('test')")
```

**Verification:**
```python
assert docs_stream.readme is not None
```

### Step 3: Assign code_stream = CodeStream(...)

```python
code_stream = CodeStream(directory=tmp_path, files=[tmp_path / 'main.py'])
```

**Verification:**
```python
assert insights_stream.metadata is not None
```

### Step 4: Assign docs_stream = DocsStream(...)

```python
docs_stream = DocsStream(readme='# Test\n\nQuick start guide.', contributing=None, docs_files=[])
```

**Verification:**
```python
assert 'Quick start guide' not in str(code_stream.files)
```

### Step 5: Assign insights_stream = InsightsStream(...)

```python
insights_stream = InsightsStream(metadata={'stars': 100}, common_problems=[], known_solutions=[], top_labels=[])
```

**Verification:**
```python
assert str(tmp_path) not in docs_stream.readme
```

### Step 6: Assign _three_streams = ThreeStreamData(...)

```python
_three_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

**Verification:**
```python
assert code_stream.directory == tmp_path
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'\n        Test that three-stream architecture produces compact, efficient output.\n\n        This is a qualitative test - we verify that output is structured and\n        not duplicated across streams.\n        '
(tmp_path / 'main.py').write_text("import os\nprint('test')")
code_stream = CodeStream(directory=tmp_path, files=[tmp_path / 'main.py'])
docs_stream = DocsStream(readme='# Test\n\nQuick start guide.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 100}, common_problems=[], known_solutions=[], top_labels=[])
_three_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
assert code_stream.directory == tmp_path
assert docs_stream.readme is not None
assert insights_stream.metadata is not None
assert 'Quick start guide' not in str(code_stream.files)
assert str(tmp_path) not in docs_stream.readme
```

## Next Steps


---

*Source: test_e2e_three_stream_pipeline.py:567 | Complexity: Intermediate | Last updated: 2026-02-14*