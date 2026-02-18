# How To: Diff Report Generation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test diff report generation.

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

### Step 1: 'Test diff report generation.'

```python
'Test diff report generation.'
```

**Verification:**
```python
assert 'INCREMENTAL UPDATE REPORT' in report
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert 'Modified: 1 files' in report
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

**Verification:**
```python
assert 'SKILL.md' in report
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
(temp_skill_dir / 'SKILL.md').write_text('# Modified content')
```

### Step 7: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 8: Assign change_set = updater2.detect_changes(...)

```python
change_set = updater2.detect_changes()
```

### Step 9: Assign report = updater2.generate_diff_report(...)

```python
report = updater2.generate_diff_report(change_set)
```

**Verification:**
```python
assert 'INCREMENTAL UPDATE REPORT' in report
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test diff report generation.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Modified content')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
report = updater2.generate_diff_report(change_set)
assert 'INCREMENTAL UPDATE REPORT' in report
assert 'Modified: 1 files' in report
assert 'SKILL.md' in report
```

## Next Steps


---

*Source: test_incremental_updates.py:212 | Complexity: Advanced | Last updated: 2026-02-14*