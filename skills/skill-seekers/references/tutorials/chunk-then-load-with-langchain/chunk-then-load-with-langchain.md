# How To: Chunk Then Load With Langchain

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that chunks can be loaded by LangChain.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test that chunks can be loaded by LangChain.'

```python
'Test that chunks can be loaded by LangChain.'
```

**Verification:**
```python
assert len(docs) > 0
```

### Step 2: Call pytest.importorskip()

```python
pytest.importorskip('langchain')
```

**Verification:**
```python
assert all((isinstance(doc, Document) for doc in docs))
```

### Step 3: Assign skill_dir = value

```python
skill_dir = tmp_path / 'test_skill'
```

### Step 4: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

### Step 5: Call unknown.write_text()

```python
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LangChain.')
```

### Step 6: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker()
```

### Step 7: Assign chunks = chunker.chunk_skill(...)

```python
chunks = chunker.chunk_skill(skill_dir)
```

### Step 8: Assign docs = value

```python
docs = [Document(page_content=chunk['page_content'], metadata=chunk['metadata']) for chunk in chunks]
```

**Verification:**
```python
assert len(docs) > 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that chunks can be loaded by LangChain.'
pytest.importorskip('langchain')
from langchain.schema import Document
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LangChain.')
chunker = RAGChunker()
chunks = chunker.chunk_skill(skill_dir)
docs = [Document(page_content=chunk['page_content'], metadata=chunk['metadata']) for chunk in chunks]
assert len(docs) > 0
assert all((isinstance(doc, Document) for doc in docs))
```

## Next Steps


---

*Source: test_rag_chunker.py:369 | Complexity: Advanced | Last updated: 2026-02-14*