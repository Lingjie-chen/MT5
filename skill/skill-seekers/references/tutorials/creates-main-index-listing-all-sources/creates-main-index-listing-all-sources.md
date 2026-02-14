# How To: Creates Main Index Listing All Sources

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that main index.md lists all documentation sources.

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

### Step 1: 'Test that main index.md lists all documentation sources.'

```python
'Test that main index.md lists all documentation sources.'
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
config = {'name': 'test_main_index', 'description': 'Test', 'sources': []}
```

### Step 7: Assign scraped_data = value

```python
scraped_data = {'documentation': [{'source_id': 'docs_one', 'base_url': 'https://one.com', 'total_pages': 10, 'refs_dir': refs_dir1}, {'source_id': 'docs_two', 'base_url': 'https://two.com', 'total_pages': 20, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
```

### Step 8: Assign builder = UnifiedSkillBuilder(...)

```python
builder = UnifiedSkillBuilder(config, scraped_data)
```

### Step 9: Call builder._generate_docs_references()

```python
builder._generate_docs_references(scraped_data['documentation'])
```

### Step 10: Assign main_index = os.path.join(...)

```python
main_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'index.md')
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(os.path.exists(main_index))
```

### Step 12: Assign content = f.read(...)

```python
content = f.read()
```

### Step 13: Call self.assertIn()

```python
self.assertIn('docs_one', content)
```

### Step 14: Call self.assertIn()

```python
self.assertIn('docs_two', content)
```

### Step 15: Call self.assertIn()

```python
self.assertIn('2 documentation sources', content)
```


## Complete Example

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

# Workflow
'Test that main index.md lists all documentation sources.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
os.makedirs(refs_dir1)
os.makedirs(refs_dir2)
config = {'name': 'test_main_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'docs_one', 'base_url': 'https://one.com', 'total_pages': 10, 'refs_dir': refs_dir1}, {'source_id': 'docs_two', 'base_url': 'https://two.com', 'total_pages': 20, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
main_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'index.md')
self.assertTrue(os.path.exists(main_index))
with open(main_index) as f:
    content = f.read()
    self.assertIn('docs_one', content)
    self.assertIn('docs_two', content)
    self.assertIn('2 documentation sources', content)
```

## Next Steps


---

*Source: test_multi_source.py:176 | Complexity: Advanced | Last updated: 2026-02-14*