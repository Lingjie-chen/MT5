# How To: Save Chunks

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test saving chunks to JSON file.

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

### Step 1: 'Test saving chunks to JSON file.'

```python
'Test saving chunks to JSON file.'
```

**Verification:**
```python
assert output_path.exists()
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker()
```

**Verification:**
```python
assert len(loaded) == 1
```

### Step 3: Assign chunks = value

```python
chunks = [{'chunk_id': 'test_0', 'page_content': 'Test content', 'metadata': {'source': 'test', 'chunk_index': 0}}]
```

**Verification:**
```python
assert loaded[0]['chunk_id'] == 'test_0'
```

### Step 4: Assign output_path = value

```python
output_path = tmp_path / 'chunks.json'
```

### Step 5: Call chunker.save_chunks()

```python
chunker.save_chunks(chunks, output_path)
```

**Verification:**
```python
assert output_path.exists()
```

### Step 6: Assign loaded = json.load(...)

```python
loaded = json.load(f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test saving chunks to JSON file.'
chunker = RAGChunker()
chunks = [{'chunk_id': 'test_0', 'page_content': 'Test content', 'metadata': {'source': 'test', 'chunk_index': 0}}]
output_path = tmp_path / 'chunks.json'
chunker.save_chunks(chunks, output_path)
assert output_path.exists()
with open(output_path) as f:
    loaded = json.load(f)
assert len(loaded) == 1
assert loaded[0]['chunk_id'] == 'test_0'
```

## Next Steps


---

*Source: test_rag_chunker.py:208 | Complexity: Intermediate | Last updated: 2026-02-14*