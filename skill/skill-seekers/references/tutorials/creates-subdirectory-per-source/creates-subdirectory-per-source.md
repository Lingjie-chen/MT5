# How To: Creates Subdirectory Per Source

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that each doc source gets its own subdirectory.

## Prerequisites

**Required Modules:**
- `os`
- `shutil`
- `tempfile`
- `unittest`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_scraper`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`
- `skill_seekers.cli.unified_skill_builder`


## Step-by-Step Guide

### Step 1: 'Test that each doc source gets its own subdirectory.'

```python
'Test that each doc source gets its own subdirectory.'
```

### Step 2: Assign refs_dir1 = os.path.join(...)

```python
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
```

### Step 3: Assign refs_dir2 = os.path.join(...)

```python
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
```

### Step 4: Call os.makedirs()

```python
os.makedirs(refs_dir1)
```

### Step 5: Call os.makedirs()

```python
os.makedirs(refs_dir2)
```

### Step 6: Assign config = value

```python
config = {'name': 'test_docs_refs', 'description': 'Test', 'sources': []}
```

### Step 7: Assign scraped_data = value

```python
scraped_data = {'documentation': [{'source_id': 'source_a', 'base_url': 'https://a.com', 'total_pages': 5, 'refs_dir': refs_dir1}, {'source_id': 'source_b', 'base_url': 'https://b.com', 'total_pages': 3, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
```

### Step 8: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 9: Call builder._generate_docs_references()

```python
builder._generate_docs_references(scraped_data['documentation'])
```

### Step 10: Assign docs_dir = os.path.join(...)

```python
docs_dir = os.path.join(builder.skill_dir, 'references', 'documentation')
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_a')))
```

### Step 12: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))
```


## Complete Example

```python
# Workflow
'Test that each doc source gets its own subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
os.makedirs(refs_dir1)
os.makedirs(refs_dir2)
config = {'name': 'test_docs_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'source_a', 'base_url': 'https://a.com', 'total_pages': 5, 'refs_dir': refs_dir1}, {'source_id': 'source_b', 'base_url': 'https://b.com', 'total_pages': 3, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
docs_dir = os.path.join(builder.skill_dir, 'references', 'documentation')
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_a')))
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))
```

## Next Steps


---

*Source: test_multi_source.py:103 | Complexity: Advanced | Last updated: 2026-02-14*