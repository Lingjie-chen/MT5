# How To: Chunk Tokens Parameter

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test --chunk-tokens parameter controls chunk size.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `json`
- `pathlib`
- `skill_seekers.cli.adaptors`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.adaptors.langchain`
- `skill_seekers.cli.package_skill`
- `skill_seekers.cli.package_skill`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test --chunk-tokens parameter controls chunk size.'

```python
'Test --chunk-tokens parameter controls chunk size.'
```

**Verification:**
```python
assert success
```

### Step 2: Assign skill_dir = create_test_skill(...)

```python
skill_dir = create_test_skill(tmp_path, large_doc=True)
```

**Verification:**
```python
assert success
```

### Step 3: Assign unknown = package_skill(...)

```python
success, package_path = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=256, preserve_code_blocks=True)
```

**Verification:**
```python
assert len(data_small) > len(data_large), f'Small chunks ({len(data_small)}) should be more than large chunks ({len(data_large)})'
```

### Step 4: Assign unknown = package_skill(...)

```python
success, package_path2 = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=1024, preserve_code_blocks=True)
```

**Verification:**
```python
assert success
```

### Step 5: Assign data_small = json.load(...)

```python
data_small = json.load(f)
```

### Step 6: Assign data_large = json.load(...)

```python
data_large = json.load(f)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test --chunk-tokens parameter controls chunk size.'
from skill_seekers.cli.package_skill import package_skill
skill_dir = create_test_skill(tmp_path, large_doc=True)
success, package_path = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=256, preserve_code_blocks=True)
assert success
with open(package_path) as f:
    data_small = json.load(f)
success, package_path2 = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=1024, preserve_code_blocks=True)
assert success
with open(package_path2) as f:
    data_large = json.load(f)
assert len(data_small) > len(data_large), f'Small chunks ({len(data_small)}) should be more than large chunks ({len(data_large)})'
```

## Next Steps


---

*Source: test_chunking_integration.py:318 | Complexity: Intermediate | Last updated: 2026-02-14*