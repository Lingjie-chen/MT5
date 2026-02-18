# How To: Detect Deleted File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of deleted files.

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

### Step 1: 'Test detection of deleted files.'

```python
'Test detection of deleted files.'
```

**Verification:**
```python
assert len(change_set.deleted) == 1
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert len(change_set.added) == 0
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

**Verification:**
```python
assert len(change_set.modified) == 0
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

**Verification:**
```python
assert 'references/getting_started.md' in change_set.deleted
```

### Step 5: Assign ref_file = value

```python
ref_file = temp_skill_dir / 'references' / 'getting_started.md'
```

### Step 6: Call ref_file.unlink()

```python
ref_file.unlink()
```

### Step 7: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 8: Assign change_set = updater2.detect_changes(...)

```python
change_set = updater2.detect_changes()
```

**Verification:**
```python
assert len(change_set.deleted) == 1
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test detection of deleted files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
ref_file = temp_skill_dir / 'references' / 'getting_started.md'
ref_file.unlink()
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.deleted) == 1
assert len(change_set.added) == 0
assert len(change_set.modified) == 0
assert 'references/getting_started.md' in change_set.deleted
```

## Next Steps


---

*Source: test_incremental_updates.py:127 | Complexity: Advanced | Last updated: 2026-02-14*