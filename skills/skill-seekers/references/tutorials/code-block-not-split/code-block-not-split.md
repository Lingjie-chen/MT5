# How To: Code Block Not Split

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that code blocks are not split across chunks.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`


## Step-by-Step Guide

### Step 1: 'Test that code blocks are not split across chunks.'

```python
'Test that code blocks are not split across chunks.'
```

**Verification:**
```python
assert code_chunk['page_content'].count('```') >= 2
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=20, preserve_code_blocks=True)
```

### Step 3: Assign text = '\n        Short intro.\n\n        ```python\n        def very_long_function_that_exceeds_chunk_size():\n            # This function is longer than our chunk size\n            # But it should not be split\n            print("Line 1")\n            print("Line 2")\n            print("Line 3")\n            return True\n        ```\n\n        Short outro.\n        '

```python
text = '\n        Short intro.\n\n        ```python\n        def very_long_function_that_exceeds_chunk_size():\n            # This function is longer than our chunk size\n            # But it should not be split\n            print("Line 1")\n            print("Line 2")\n            print("Line 3")\n            return True\n        ```\n\n        Short outro.\n        '
```

### Step 4: Assign chunks = chunker.chunk_document(...)

```python
chunks = chunker.chunk_document(text, {'source': 'test'})
```

### Step 5: Assign code_chunks = value

```python
code_chunks = [c for c in chunks if '```python' in c['page_content']]
```

### Step 6: Assign code_chunk = value

```python
code_chunk = code_chunks[0]
```

**Verification:**
```python
assert code_chunk['page_content'].count('```') >= 2
```


## Complete Example

```python
# Workflow
'Test that code blocks are not split across chunks.'
chunker = RAGChunker(chunk_size=20, preserve_code_blocks=True)
text = '\n        Short intro.\n\n        ```python\n        def very_long_function_that_exceeds_chunk_size():\n            # This function is longer than our chunk size\n            # But it should not be split\n            print("Line 1")\n            print("Line 2")\n            print("Line 3")\n            return True\n        ```\n\n        Short outro.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
code_chunks = [c for c in chunks if '```python' in c['page_content']]
if code_chunks:
    code_chunk = code_chunks[0]
    assert code_chunk['page_content'].count('```') >= 2
```

## Next Steps


---

*Source: test_rag_chunker.py:110 | Complexity: Intermediate | Last updated: 2026-02-14*