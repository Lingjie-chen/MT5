# How To: Generate Update Package

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test update package generation.

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

### Step 1: 'Test update package generation.'

```python
'Test update package generation.'
```

**Verification:**
```python
assert result_path.exists()
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert 'metadata' in package_data
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

**Verification:**
```python
assert 'changes' in package_data
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

**Verification:**
```python
assert package_data['metadata']['total_changes'] == 1
```

### Step 5: Call time.sleep()

```python
time.sleep(0.01)
```

**Verification:**
```python
assert 'SKILL.md' in package_data['changes']
```

### Step 6: Call unknown.write_text()

```python
(temp_skill_dir / 'SKILL.md').write_text('# Modified')
```

**Verification:**
```python
assert package_data['changes']['SKILL.md']['action'] == 'modify'
```

### Step 7: Assign updater2 = IncrementalUpdater(...)

```python
updater2 = IncrementalUpdater(temp_skill_dir)
```

### Step 8: Assign change_set = updater2.detect_changes(...)

```python
change_set = updater2.detect_changes()
```

### Step 9: Assign package_path = value

```python
package_path = Path(tmpdir) / 'update.json'
```

### Step 10: Assign result_path = updater2.generate_update_package(...)

```python
result_path = updater2.generate_update_package(change_set, package_path)
```

**Verification:**
```python
assert result_path.exists()
```

### Step 11: Assign package_data = json.loads(...)

```python
package_data = json.loads(result_path.read_text())
```

**Verification:**
```python
assert 'metadata' in package_data
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test update package generation.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Modified')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
with tempfile.TemporaryDirectory() as tmpdir:
    package_path = Path(tmpdir) / 'update.json'
    result_path = updater2.generate_update_package(change_set, package_path)
    assert result_path.exists()
    package_data = json.loads(result_path.read_text())
    assert 'metadata' in package_data
    assert 'changes' in package_data
    assert package_data['metadata']['total_changes'] == 1
    assert 'SKILL.md' in package_data['changes']
    assert package_data['changes']['SKILL.md']['action'] == 'modify'
```

## Next Steps


---

*Source: test_incremental_updates.py:180 | Complexity: Advanced | Last updated: 2026-02-14*