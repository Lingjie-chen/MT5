# How To: Chroma Query Filtering

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test metadata filtering in ChromaDB queries.

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
# Fixtures: sample_skill_dir, tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test metadata filtering in ChromaDB queries.'

```python
'Test metadata filtering in ChromaDB queries.'
```

**Verification:**
```python
assert len(results['documents']) > 0, 'No documents matched filter'
```

### Step 2: Assign adaptor = get_adaptor(...)

```python
adaptor = get_adaptor('chroma')
```

**Verification:**
```python
assert metadata['category'] == 'getting started', 'Filter returned wrong category'
```

### Step 3: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='chroma_filter_test', description='Test filtering capabilities')
```

### Step 4: Assign package_path = adaptor.package(...)

```python
package_path = adaptor.package(sample_skill_dir, tmp_path)
```

### Step 5: Assign collection_name = value

```python
collection_name = data['collection_name']
```

### Step 6: Call pytest.skip()

```python
pytest.skip('ChromaDB not running')
```

### Step 7: Assign client = chromadb.HttpClient(...)

```python
client = chromadb.HttpClient(host='localhost', port=8000)
```

### Step 8: Call client.heartbeat()

```python
client.heartbeat()
```

### Step 9: Assign data = json.load(...)

```python
data = json.load(f)
```

### Step 10: Assign collection = client.get_or_create_collection(...)

```python
collection = client.get_or_create_collection(name=collection_name)
```

### Step 11: Call collection.add()

```python
collection.add(documents=data['documents'], metadatas=data['metadatas'], ids=data['ids'])
```

### Step 12: Call time.sleep()

```python
time.sleep(1)
```

### Step 13: Assign results = collection.get(...)

```python
results = collection.get(where={'category': 'getting started'})
```

**Verification:**
```python
assert len(results['documents']) > 0, 'No documents matched filter'
```

### Step 14: Call pytest.skip()

```python
pytest.skip('chromadb not installed')
```

### Step 15: Call pytest.skip()

```python
pytest.skip(f'Cannot connect to ChromaDB: {e}')
```

**Verification:**
```python
assert metadata['category'] == 'getting started', 'Filter returned wrong category'
```

### Step 16: Call client.delete_collection()

```python
client.delete_collection(name=collection_name)
```


## Complete Example

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

# Workflow
'Test metadata filtering in ChromaDB queries.'
try:
    import chromadb
except ImportError:
    pytest.skip('chromadb not installed')
if not check_service_available('http://localhost:8000/api/v1/heartbeat'):
    pytest.skip('ChromaDB not running')
try:
    client = chromadb.HttpClient(host='localhost', port=8000)
    client.heartbeat()
except Exception as e:
    pytest.skip(f'Cannot connect to ChromaDB: {e}')
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='chroma_filter_test', description='Test filtering capabilities')
package_path = adaptor.package(sample_skill_dir, tmp_path)
with open(package_path) as f:
    data = json.load(f)
collection_name = data['collection_name']
try:
    collection = client.get_or_create_collection(name=collection_name)
    collection.add(documents=data['documents'], metadatas=data['metadatas'], ids=data['ids'])
    time.sleep(1)
    results = collection.get(where={'category': 'getting started'})
    assert len(results['documents']) > 0, 'No documents matched filter'
    for metadata in results['metadatas']:
        assert metadata['category'] == 'getting started', 'Filter returned wrong category'
finally:
    with contextlib.suppress(Exception):
        client.delete_collection(name=collection_name)
```

## Next Steps


---

*Source: test_integration_adaptors.py:357 | Complexity: Advanced | Last updated: 2026-02-14*