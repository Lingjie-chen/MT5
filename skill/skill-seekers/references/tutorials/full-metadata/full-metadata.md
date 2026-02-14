# How To: Full Metadata

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test metadata with all fields

## Prerequisites

**Required Modules:**
- `unittest`
- `skill_seekers.cli.adaptors`


## Step-by-Step Guide

### Step 1: 'Test metadata with all fields'

```python
'Test metadata with all fields'
```

### Step 2: Assign metadata = SkillMetadata(...)

```python
metadata = SkillMetadata(name='react', description='React documentation', version='2.5.0', author='Test Author', tags=['react', 'javascript', 'web'])
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(metadata.name, 'react')
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(metadata.description, 'React documentation')
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(metadata.version, '2.5.0')
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(metadata.author, 'Test Author')
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])
```


## Complete Example

```python
# Workflow
'Test metadata with all fields'
metadata = SkillMetadata(name='react', description='React documentation', version='2.5.0', author='Test Author', tags=['react', 'javascript', 'web'])
self.assertEqual(metadata.name, 'react')
self.assertEqual(metadata.description, 'React documentation')
self.assertEqual(metadata.version, '2.5.0')
self.assertEqual(metadata.author, 'Test Author')
self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])
```

## Next Steps


---

*Source: test_base.py:30 | Complexity: Intermediate | Last updated: 2026-02-14*