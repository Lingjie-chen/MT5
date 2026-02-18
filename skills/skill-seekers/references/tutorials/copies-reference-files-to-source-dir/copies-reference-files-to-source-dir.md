# How To: Copies Reference Files To Source Dir

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that reference files are copied to source subdirectory.

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

### Step 1: 'Test that reference files are copied to source subdirectory.'

```python
'Test that reference files are copied to source subdirectory.'
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
config = {'name': 'test_copy_refs', 'description': 'Test', 'sources': []}
```

### Step 5: Assign scraped_data = value

```python
scraped_data = {'documentation': [{'source_id': 'test_source', 'base_url': 'https://test.com', 'total_pages': 5, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
```

### Step 6: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 7: Call builder._generate_docs_references()

```python
builder._generate_docs_references(scraped_data['documentation'])
```

### Step 8: Assign source_dir = os.path.join(...)

```python
source_dir = os.path.join(builder.skill_dir, 'references', 'documentation', 'test_source')
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(source_dir, 'api.md')))
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(os.path.join(source_dir, 'guide.md')))
```

### Step 11: Call f.write()

```python
f.write('# API Reference')
```

### Step 12: Call f.write()

```python
f.write('# User Guide')
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that reference files are copied to source subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir = os.path.join(self.temp_dir, 'refs')
os.makedirs(refs_dir)
with open(os.path.join(refs_dir, 'api.md'), 'w') as f:
    f.write('# API Reference')
with open(os.path.join(refs_dir, 'guide.md'), 'w') as f:
    f.write('# User Guide')
config = {'name': 'test_copy_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'test_source', 'base_url': 'https://test.com', 'total_pages': 5, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
source_dir = os.path.join(builder.skill_dir, 'references', 'documentation', 'test_source')
self.assertTrue(os.path.exists(os.path.join(source_dir, 'api.md')))
self.assertTrue(os.path.exists(os.path.join(source_dir, 'guide.md')))
```

## Next Steps


---

*Source: test_multi_source.py:218 | Complexity: Advanced | Last updated: 2026-02-14*