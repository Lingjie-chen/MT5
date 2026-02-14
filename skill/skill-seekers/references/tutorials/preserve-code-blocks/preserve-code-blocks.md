# How To: Preserve Code Blocks

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test code block preservation.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`


## Step-by-Step Guide

### Step 1: 'Test code block preservation.'

```python
'Test code block preservation.'
```

**Verification:**
```python
assert has_code
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=50, preserve_code_blocks=True)
```

**Verification:**
```python
assert len(code_chunks) > 0
```

### Step 3: Assign text = '\n        Here is some text.\n\n        ```python\n        def hello():\n            print("Hello, world!")\n        ```\n\n        More text here.\n        '

```python
text = '\n        Here is some text.\n\n        ```python\n        def hello():\n            print("Hello, world!")\n        ```\n\n        More text here.\n        '
```

### Step 4: Assign chunks = chunker.chunk_document(...)

```python
chunks = chunker.chunk_document(text, {'source': 'test'})
```

### Step 5: Assign has_code = any(...)

```python
has_code = any(('```' in chunk['page_content'] for chunk in chunks))
```

**Verification:**
```python
assert has_code
```

### Step 6: Assign code_chunks = value

```python
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
```

**Verification:**
```python
assert len(code_chunks) > 0
```


## Complete Example

```python
# Workflow
'Test code block preservation.'
chunker = RAGChunker(chunk_size=50, preserve_code_blocks=True)
text = '\n        Here is some text.\n\n        ```python\n        def hello():\n            print("Hello, world!")\n        ```\n\n        More text here.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
has_code = any(('```' in chunk['page_content'] for chunk in chunks))
assert has_code
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
assert len(code_chunks) > 0
```

## Next Steps


---

*Source: test_rag_chunker.py:85 | Complexity: Intermediate | Last updated: 2026-02-14*