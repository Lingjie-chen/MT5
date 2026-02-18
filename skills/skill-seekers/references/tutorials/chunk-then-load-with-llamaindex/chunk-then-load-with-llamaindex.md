# How To: Chunk Then Load With Llamaindex

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that chunks can be loaded by LlamaIndex.

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

### Step 1: 'Test that chunks can be loaded by LlamaIndex.'

```python
'Test that chunks can be loaded by LlamaIndex.'
```

**Verification:**
```python
assert len(nodes) > 0
```

### Step 2: Call pytest.importorskip()

```python
pytest.importorskip('llama_index')
```

**Verification:**
```python
assert all((isinstance(node, TextNode) for node in nodes))
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
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LlamaIndex.')
```

### Step 6: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker()
```

### Step 7: Assign chunks = chunker.chunk_skill(...)

```python
chunks = chunker.chunk_skill(skill_dir)
```

### Step 8: Assign nodes = value

```python
nodes = [TextNode(text=chunk['page_content'], metadata=chunk['metadata'], id_=chunk['chunk_id']) for chunk in chunks]
```

**Verification:**
```python
assert len(nodes) > 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test that chunks can be loaded by LlamaIndex.'
pytest.importorskip('llama_index')
from llama_index.core.schema import TextNode
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LlamaIndex.')
chunker = RAGChunker()
chunks = chunker.chunk_skill(skill_dir)
nodes = [TextNode(text=chunk['page_content'], metadata=chunk['metadata'], id_=chunk['chunk_id']) for chunk in chunks]
assert len(nodes) > 0
assert all((isinstance(node, TextNode) for node in nodes))
```

## Next Steps


---

*Source: test_rag_chunker.py:394 | Complexity: Advanced | Last updated: 2026-02-14*