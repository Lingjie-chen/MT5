# How To: Semantic Boundaries

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that chunks respect paragraph boundaries.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`


## Step-by-Step Guide

### Step 1: 'Test that chunks respect paragraph boundaries.'

```python
'Test that chunks respect paragraph boundaries.'
```

**Verification:**
```python
assert not content.strip().endswith(',')
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=50, preserve_paragraphs=True)
```

### Step 3: Assign text = '\n        First paragraph here.\n        It has multiple sentences.\n\n        Second paragraph here.\n        Also with multiple sentences.\n\n        Third paragraph.\n        '

```python
text = '\n        First paragraph here.\n        It has multiple sentences.\n\n        Second paragraph here.\n        Also with multiple sentences.\n\n        Third paragraph.\n        '
```

### Step 4: Assign chunks = chunker.chunk_document(...)

```python
chunks = chunker.chunk_document(text, {'source': 'test'})
```

### Step 5: Assign content = value

```python
content = chunk['page_content']
```

**Verification:**
```python
assert not content.strip().endswith(',')
```


## Complete Example

```python
# Workflow
'Test that chunks respect paragraph boundaries.'
chunker = RAGChunker(chunk_size=50, preserve_paragraphs=True)
text = '\n        First paragraph here.\n        It has multiple sentences.\n\n        Second paragraph here.\n        Also with multiple sentences.\n\n        Third paragraph.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
for chunk in chunks:
    content = chunk['page_content']
    if content.strip():
        assert not content.strip().endswith(',')
```

## Next Steps


---

*Source: test_rag_chunker.py:140 | Complexity: Intermediate | Last updated: 2026-02-14*