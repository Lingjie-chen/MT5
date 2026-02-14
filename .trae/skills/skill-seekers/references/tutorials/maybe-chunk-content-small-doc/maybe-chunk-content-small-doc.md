# How To: Maybe Chunk Content Small Doc

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that small docs are not chunked even when enabled.

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

### Step 1: 'Test that small docs are not chunked even when enabled.'

```python
'Test that small docs are not chunked even when enabled.'
```

**Verification:**
```python
assert len(chunks) == 1
```

### Step 2: Assign adaptor = LangChainAdaptor(...)

```python
adaptor = LangChainAdaptor()
```

### Step 3: Assign content = 'Small test content'

```python
content = 'Small test content'
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test'}
```

### Step 5: Assign chunks = adaptor._maybe_chunk_content(...)

```python
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512)
```

**Verification:**
```python
assert len(chunks) == 1
```


## Complete Example

```python
# Workflow
'Test that small docs are not chunked even when enabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Small test content'
metadata = {'source': 'test'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512)
assert len(chunks) == 1
```

## Next Steps


---

*Source: test_chunking_integration.py:241 | Complexity: Intermediate | Last updated: 2026-02-14*