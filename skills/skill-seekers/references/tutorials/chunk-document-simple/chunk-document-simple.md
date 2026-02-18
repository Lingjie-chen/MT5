# How To: Chunk Document Simple

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test chunking simple document.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`


## Step-by-Step Guide

### Step 1: 'Test chunking simple document.'

```python
'Test chunking simple document.'
```

**Verification:**
```python
assert len(chunks) > 0
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=50, chunk_overlap=10)
```

**Verification:**
```python
assert all(('chunk_id' in chunk for chunk in chunks))
```

### Step 3: Assign text = 'This is a simple document.\n\nIt has two paragraphs.\n\nAnd a third one.'

```python
text = 'This is a simple document.\n\nIt has two paragraphs.\n\nAnd a third one.'
```

**Verification:**
```python
assert all(('page_content' in chunk for chunk in chunks))
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'test', 'category': 'simple'}
```

**Verification:**
```python
assert all(('metadata' in chunk for chunk in chunks))
```

### Step 5: Assign chunks = chunker.chunk_document(...)

```python
chunks = chunker.chunk_document(text, metadata)
```

**Verification:**
```python
assert chunk['metadata']['source'] == 'test'
```


## Complete Example

```python
# Workflow
'Test chunking simple document.'
chunker = RAGChunker(chunk_size=50, chunk_overlap=10)
text = 'This is a simple document.\n\nIt has two paragraphs.\n\nAnd a third one.'
metadata = {'source': 'test', 'category': 'simple'}
chunks = chunker.chunk_document(text, metadata)
assert len(chunks) > 0
assert all(('chunk_id' in chunk for chunk in chunks))
assert all(('page_content' in chunk for chunk in chunks))
assert all(('metadata' in chunk for chunk in chunks))
for i, chunk in enumerate(chunks):
    assert chunk['metadata']['source'] == 'test'
    assert chunk['metadata']['category'] == 'simple'
    assert chunk['metadata']['chunk_index'] == i
    assert chunk['metadata']['total_chunks'] == len(chunks)
```

## Next Steps


---

*Source: test_rag_chunker.py:64 | Complexity: Intermediate | Last updated: 2026-02-14*