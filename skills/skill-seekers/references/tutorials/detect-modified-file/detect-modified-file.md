# How To: Detect Modified File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test detection of modified files.

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

### Step 1: 'Test detection of modified files.'

```python
'Test detection of modified files.'
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
assert len(change_set.added) == 0
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
assert change_set.modified[0].file_path == 'SKILL.md'
```

### Step 5: Call time.sleep()

```python
time.sleep(0.01)
```

**Verification:**
```python
assert change_set.modified[0].version == 2
```

### Step 6: Assign skill_md = value

```python
skill_md = temp_skill_dir / 'SKILL.md'
```

### Step 7: Call skill_md.write_text()

```python
skill_md.write_text('# Test Skill\n\nModified content')
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
assert len(change_set.modified) == 1
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test detection of modified files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
skill_md = temp_skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nModified content')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.modified) == 1
assert len(change_set.added) == 0
assert len(change_set.deleted) == 0
assert change_set.modified[0].file_path == 'SKILL.md'
assert change_set.modified[0].version == 2
```

## Next Steps


---

*Source: test_incremental_updates.py:80 | Complexity: Advanced | Last updated: 2026-02-14*