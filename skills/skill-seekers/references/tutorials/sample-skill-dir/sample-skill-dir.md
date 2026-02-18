# How To: Sample Skill Dir

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Create a sample skill for integration testing.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `time`
- `pytest`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.adaptors.base`
- `contextlib`
- `sys`
- `requests`
- `weaviate`
- `weaviate`
- `chromadb`
- `chromadb`
- `qdrant_client`
- `qdrant_client.models`
- `qdrant_client`
- `qdrant_client.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Create a sample skill for integration testing.'

```python
'Create a sample skill for integration testing.'
```

### Step 2: Assign skill_dir = value

```python
skill_dir = tmp_path / 'test_integration_skill'
```

### Step 3: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

### Step 4: Assign skill_md = '# Integration Test Skill\n\nThis is a test skill for integration testing with vector databases.\n\n## Core Concepts\n\n- Concept 1: Understanding vector embeddings\n- Concept 2: Similarity search algorithms\n- Concept 3: Metadata filtering\n\n## Quick Start\n\nGet started with vector databases in 3 steps:\n1. Initialize your database\n2. Upload your documents\n3. Query with semantic search\n'

```python
skill_md = '# Integration Test Skill\n\nThis is a test skill for integration testing with vector databases.\n\n## Core Concepts\n\n- Concept 1: Understanding vector embeddings\n- Concept 2: Similarity search algorithms\n- Concept 3: Metadata filtering\n\n## Quick Start\n\nGet started with vector databases in 3 steps:\n1. Initialize your database\n2. Upload your documents\n3. Query with semantic search\n'
```

### Step 5: Call unknown.write_text()

```python
(skill_dir / 'SKILL.md').write_text(skill_md)
```

### Step 6: Assign refs_dir = value

```python
refs_dir = skill_dir / 'references'
```

### Step 7: Call refs_dir.mkdir()

```python
refs_dir.mkdir()
```

### Step 8: Assign references = value

```python
references = {'api_reference.md': '# API Reference\n\n## Core Functions\n\n### add_documents(documents, metadata)\nAdd documents to the vector database.\n\n### query(text, limit=10)\nQuery the database with semantic search.\n\n### delete_collection(name)\nDelete a collection from the database.\n', 'getting_started.md': '# Getting Started\n\n## Installation\n\n```bash\npip install vector-db-client\n```\n\n## Basic Usage\n\n```python\nfrom vector_db import Client\n\nclient = Client("http://localhost:8080")\nclient.add_documents(["doc1", "doc2"])\nresults = client.query("search query")\n```\n', 'advanced_features.md': '# Advanced Features\n\n## Hybrid Search\n\nCombine keyword and vector search for better results.\n\n## Metadata Filtering\n\nFilter results based on metadata attributes.\n\n## Multi-modal Search\n\nSearch across text, images, and audio.\n'}
```

### Step 9: Call unknown.write_text()

```python
(refs_dir / filename).write_text(content)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Create a sample skill for integration testing.'
skill_dir = tmp_path / 'test_integration_skill'
skill_dir.mkdir()
skill_md = '# Integration Test Skill\n\nThis is a test skill for integration testing with vector databases.\n\n## Core Concepts\n\n- Concept 1: Understanding vector embeddings\n- Concept 2: Similarity search algorithms\n- Concept 3: Metadata filtering\n\n## Quick Start\n\nGet started with vector databases in 3 steps:\n1. Initialize your database\n2. Upload your documents\n3. Query with semantic search\n'
(skill_dir / 'SKILL.md').write_text(skill_md)
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
references = {'api_reference.md': '# API Reference\n\n## Core Functions\n\n### add_documents(documents, metadata)\nAdd documents to the vector database.\n\n### query(text, limit=10)\nQuery the database with semantic search.\n\n### delete_collection(name)\nDelete a collection from the database.\n', 'getting_started.md': '# Getting Started\n\n## Installation\n\n```bash\npip install vector-db-client\n```\n\n## Basic Usage\n\n```python\nfrom vector_db import Client\n\nclient = Client("http://localhost:8080")\nclient.add_documents(["doc1", "doc2"])\nresults = client.query("search query")\n```\n', 'advanced_features.md': '# Advanced Features\n\n## Hybrid Search\n\nCombine keyword and vector search for better results.\n\n## Metadata Filtering\n\nFilter results based on metadata attributes.\n\n## Multi-modal Search\n\nSearch across text, images, and audio.\n'}
for filename, content in references.items():
    (refs_dir / filename).write_text(content)
return skill_dir
```

## Next Steps


---

*Source: test_integration_adaptors.py:29 | Complexity: Advanced | Last updated: 2026-02-14*