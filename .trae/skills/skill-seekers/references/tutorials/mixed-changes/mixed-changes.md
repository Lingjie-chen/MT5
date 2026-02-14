# How To: Mixed Changes

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of multiple types of changes.

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

### Step 1: 'Test detection of multiple types of changes.'

```python
'Test detection of multiple types of changes.'
```

**Verification:**
```python
assert len(change_set.modified) == 1
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert len(change_set.added) == 1
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

**Verification:**
```python
assert len(change_set.deleted) == 1
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

**Verification:**
```python
assert change_set.total_changes == 3
```

### Step 5: Call time.sleep()

```python
time.sleep(0.01)
```

### Step 6: Call unknown.write_text()

```python
(temp_skill_dir / 'SKILL.md').write_text('# Test Skill\n\nModified')
```

### Step 7: Assign refs_dir = value

```python
refs_dir = temp_skill_dir / 'references'
```

### Step 8: Call unknown.write_text()

```python
(refs_dir / 'new_file.md').write_text('# New File')
```

### Step 9: Call unknown.unlink()

```python
(refs_dir / 'getting_started.md').unlink()
```

### Step 10: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 11: Assign change_set = updater2.detect_changes(...)

```python
change_set = updater2.detect_changes()
```

**Verification:**
```python
assert len(change_set.modified) == 1
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test detection of multiple types of changes.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Test Skill\n\nModified')
refs_dir = temp_skill_dir / 'references'
(refs_dir / 'new_file.md').write_text('# New File')
(refs_dir / 'getting_started.md').unlink()
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.modified) == 1
assert len(change_set.added) == 1
assert len(change_set.deleted) == 1
assert change_set.total_changes == 3
```

## Next Steps


---

*Source: test_incremental_updates.py:149 | Complexity: Advanced | Last updated: 2026-02-14*