# How To: Version Increment

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test version numbers increment correctly.

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

### Step 1: 'Test version numbers increment correctly.'

```python
'Test version numbers increment correctly.'
```

**Verification:**
```python
assert doc.version == 1
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert change_set2.modified[0].version == 2
```

### Step 3: Assign change_set1 = updater.detect_changes(...)

```python
change_set1 = updater.detect_changes()
```

**Verification:**
```python
assert change_set3.modified[0].version == 3
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

### Step 5: Call time.sleep()

```python
time.sleep(0.01)
```

### Step 6: Call unknown.write_text()

```python
(temp_skill_dir / 'SKILL.md').write_text('Modified once')
```

### Step 7: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 8: Assign change_set2 = updater2.detect_changes(...)

```python
change_set2 = updater2.detect_changes()
```

### Step 9: Call updater2.save_current_versions()

```python
updater2.save_current_versions()
```

**Verification:**
```python
assert change_set2.modified[0].version == 2
```

### Step 10: Call time.sleep()

```python
time.sleep(0.01)
```

### Step 11: Call unknown.write_text()

```python
(temp_skill_dir / 'SKILL.md').write_text('Modified twice')
```

### Step 12: Assign updater3 = IncrementalUpdater(...)

```python
updater3 = IncrementalUpdater(temp_skill_dir)
```

### Step 13: Assign change_set3 = updater3.detect_changes(...)

```python
change_set3 = updater3.detect_changes()
```

**Verification:**
```python
assert change_set3.modified[0].version == 3
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test version numbers increment correctly.'
updater = IncrementalUpdater(temp_skill_dir)
change_set1 = updater.detect_changes()
updater.save_current_versions()
for doc in change_set1.added:
    assert doc.version == 1
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('Modified once')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set2 = updater2.detect_changes()
updater2.save_current_versions()
assert change_set2.modified[0].version == 2
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('Modified twice')
updater3 = IncrementalUpdater(temp_skill_dir)
change_set3 = updater3.detect_changes()
assert change_set3.modified[0].version == 3
```

## Next Steps


---

*Source: test_incremental_updates.py:234 | Complexity: Advanced | Last updated: 2026-02-14*