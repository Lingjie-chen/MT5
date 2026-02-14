# How To: Chunk Skill Directory

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test chunking entire skill directory.

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

### Step 1: 'Test chunking entire skill directory.'

```python
'Test chunking entire skill directory.'
```

**Verification:**
```python
assert len(chunks) > 0
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'test_skill'
```

**Verification:**
```python
assert 'overview' in categories
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert 'getting_started' in categories or 'api' in categories
```

### Step 4: Assign skill_md = value

```python
skill_md = skill_dir / 'SKILL.md'
```

### Step 5: Call skill_md.write_text()

```python
skill_md.write_text('# Main Skill\n\nThis is the main skill content.\n\nWith multiple paragraphs.')
```

### Step 6: Assign references_dir = value

```python
references_dir = skill_dir / 'references'
```

### Step 7: Call references_dir.mkdir()

```python
references_dir.mkdir()
```

### Step 8: Call unknown.write_text()

```python
(references_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start guide.')
```

### Step 9: Call unknown.write_text()

```python
(references_dir / 'api.md').write_text('# API Reference\n\nAPI documentation.')
```

### Step 10: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=50)
```

### Step 11: Assign chunks = chunker.chunk_skill(...)

```python
chunks = chunker.chunk_skill(skill_dir)
```

**Verification:**
```python
assert len(chunks) > 0
```

### Step 12: Assign categories = value

```python
categories = {chunk['metadata']['category'] for chunk in chunks}
```

**Verification:**
```python
assert 'overview' in categories
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test chunking entire skill directory.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Main Skill\n\nThis is the main skill content.\n\nWith multiple paragraphs.')
references_dir = skill_dir / 'references'
references_dir.mkdir()
(references_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start guide.')
(references_dir / 'api.md').write_text('# API Reference\n\nAPI documentation.')
chunker = RAGChunker(chunk_size=50)
chunks = chunker.chunk_skill(skill_dir)
assert len(chunks) > 0
categories = {chunk['metadata']['category'] for chunk in chunks}
assert 'overview' in categories
assert 'getting_started' in categories or 'api' in categories
```

## Next Steps


---

*Source: test_rag_chunker.py:175 | Complexity: Advanced | Last updated: 2026-02-14*