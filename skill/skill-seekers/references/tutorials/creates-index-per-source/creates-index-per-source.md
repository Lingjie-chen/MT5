# How To: Creates Index Per Source

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that each source subdirectory has its own index.md.

## Prerequisites

- [ ] Setup code must be executed first

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

**Setup Required:**
```python
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)
```

## Step-by-Step Guide

### Step 1: 'Test that each source subdirectory has its own index.md.'

```python
'Test that each source subdirectory has its own index.md.'
```

### Step 2: Assign refs_dir = os.path.join(...)

```python
refs_dir = os.path.join(self.temp_dir, 'refs')
```

### Step 3: Call os.makedirs()

```python
os.makedirs(refs_dir)
```

### Step 4: Assign config = value

```python
config = {'name': 'test_source_index', 'description': 'Test', 'sources': []}
```

### Step 5: Assign scraped_data = value

```python
scraped_data = {'documentation': [{'source_id': 'my_source', 'base_url': 'https://example.com', 'total_pages': 10, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
```

### Step 6: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 7: Call builder._generate_docs_references()

```python
builder._generate_docs_references(scraped_data['documentation'])
```

### Step 8: Assign source_index = os.path.join(...)

```python
source_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'my_source', 'index.md')
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(source_index))
```

### Step 10: Assign content = f.read(...)

```python
content = f.read()
```

### Step 11: Call self.assertIn()

```python
self.assertIn('my_source', content)
```

### Step 12: Call self.assertIn()

```python
self.assertIn('https://example.com', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that each source subdirectory has its own index.md.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir = os.path.join(self.temp_dir, 'refs')
os.makedirs(refs_dir)
config = {'name': 'test_source_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'my_source', 'base_url': 'https://example.com', 'total_pages': 10, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
source_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'my_source', 'index.md')
self.assertTrue(os.path.exists(source_index))
with open(source_index) as f:
    content = f.read()
    self.assertIn('my_source', content)
    self.assertIn('https://example.com', content)
```

## Next Steps


---

*Source: test_multi_source.py:141 | Complexity: Advanced | Last updated: 2026-02-14*