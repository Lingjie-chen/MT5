# How To: Apply Update Package

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test applying an update package.

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

### Step 1: 'Test applying an update package.'

```python
'Test applying an update package.'
```

**Verification:**
```python
assert success
```

### Step 2: Assign updater = IncrementalUpdater(...)

```python
updater = IncrementalUpdater(temp_skill_dir)
```

**Verification:**
```python
assert (temp_skill_dir / 'SKILL.md').read_text() == '# Updated Content\n\nApplied from package'
```

### Step 3: Call updater.detect_changes()

```python
updater.detect_changes()
```

### Step 4: Call updater.save_current_versions()

```python
updater.save_current_versions()
```

### Step 5: Assign package_path = value

```python
package_path = Path(tmpdir) / 'update.json'
```

### Step 6: Assign update_data = value

```python
update_data = {'metadata': {'timestamp': '2026-02-05T12:00:00', 'skill_name': 'test_skill', 'change_summary': {'modified': 1}, 'total_changes': 1}, 'changes': {'SKILL.md': {'action': 'modify', 'version': 2, 'content': '# Updated Content\n\nApplied from package'}}}
```

### Step 7: Call package_path.write_text()

```python
package_path.write_text(json.dumps(update_data))
```

### Step 8: Assign success = updater.apply_update_package(...)

```python
success = updater.apply_update_package(package_path)
```

**Verification:**
```python
assert success
```


## Complete Example

```python
# Setup
# Fixtures: temp_skill_dir

# Workflow
'Test applying an update package.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
with tempfile.TemporaryDirectory() as tmpdir:
    package_path = Path(tmpdir) / 'update.json'
    update_data = {'metadata': {'timestamp': '2026-02-05T12:00:00', 'skill_name': 'test_skill', 'change_summary': {'modified': 1}, 'total_changes': 1}, 'changes': {'SKILL.md': {'action': 'modify', 'version': 2, 'content': '# Updated Content\n\nApplied from package'}}}
    package_path.write_text(json.dumps(update_data))
    success = updater.apply_update_package(package_path)
    assert success
    assert (temp_skill_dir / 'SKILL.md').read_text() == '# Updated Content\n\nApplied from package'
```

## Next Steps


---

*Source: test_incremental_updates.py:266 | Complexity: Advanced | Last updated: 2026-02-14*