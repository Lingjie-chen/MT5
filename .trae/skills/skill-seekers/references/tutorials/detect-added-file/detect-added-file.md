# How To: Detect Added File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of new files.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `sys`
- `tempfile`
- `json`
- `time`
- `skill_seekers.cli.incremental_updater`

**Setup Required:**
```python
# Fixtures: temp_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Test detection of new files.'

```python
'Test detection of new files.'
```

**Verification:**
```python
assert len(change_set.added) == 1
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert len(change_set.modified) == 0
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

**Verification:**
```python
assert len(change_set.deleted) == 0
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

**Verification:**
```python
assert change_set.added[0].file_path == 'references/api_reference.md'
```

### Step 5: Assign refs_dir = value

```python
refs_dir = temp_skill_dir / 'references'
```

### Step 6: Assign new_ref = value

```python
new_ref = refs_dir / 'api_reference.md'
```

### Step 7: Call new_ref.write_text()

```python
new_ref.write_text('# API Reference\n\nNew documentation')
```

### Step 8: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 9: Assign change_set = updater2.detect_changes(...)

```python
change_set = updater2.detect_changes()
```

**Verification:**
```python
assert len(change_set.added) == 1
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test detection of new files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
refs_dir = temp_skill_dir / 'references'
new_ref = refs_dir / 'api_reference.md'
new_ref.write_text('# API Reference\n\nNew documentation')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.added) == 1
assert len(change_set.modified) == 0
assert len(change_set.deleted) == 0
assert change_set.added[0].file_path == 'references/api_reference.md'
```

## Next Steps


---

*Source: test_incremental_updates.py:104 | Complexity: Advanced | Last updated: 2026-02-14*