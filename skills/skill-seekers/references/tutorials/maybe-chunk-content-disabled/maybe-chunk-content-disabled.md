# How To: Maybe Chunk Content Disabled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that _maybe_chunk_content returns single chunk when disabled.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `pathlib`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.package_skill`


## Step-by-Step Guide

### Step 1: 'Test that _maybe_chunk_content returns single chunk when disabled.'

```python
'Test that _maybe_chunk_content returns single chunk when disabled.'
```

**Verification:**
```python
assert len(chunks) == 1
```

### Step 2: Assign adaptor = LangChainAdaptor(...)

```python
adaptor = LangChainAdaptor()
```

**Verification:**
```python
assert chunks[0][0] == content
```

### Step 3: Assign content = value

```python
content = 'Test content ' * 1000
```

**Verification:**
```python
assert chunks[0][1] == metadata
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test'}
```

### Step 5: Assign chunks = adaptor._maybe_chunk_content(...)

```python
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=False)
```

**Verification:**
```python
assert len(chunks) == 1
```


## Complete Example

```python
# Workflow
'Test that _maybe_chunk_content returns single chunk when disabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Test content ' * 1000
metadata = {'source': 'test'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=False)
assert len(chunks) == 1
assert chunks[0][0] == content
assert chunks[0][1] == metadata
```

## Next Steps


---

*Source: test_chunking_integration.py:225 | Complexity: Intermediate | Last updated: 2026-02-14*